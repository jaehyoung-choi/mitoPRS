import joblib
import os
import sys
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
import mitoprs_utils as utils
sys.modules['enet_utils'] = utils
# This import is vital: it provides load_data_split_median AND InformedElasticNet
from mitoprs_utils import InformedElasticNet

def main():
    # Hardcoded paths as requested
    XGB_PATH = "model/0.15_xgb_model.pkl"
    ENET_PATH = "model/0.3_enet_model.pkl"
    
    #Making output directory if doesn't exist
    output_dir = "./output"
    os.makedirs("output", exist_ok=True)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ext-feature', required=True)
    parser.add_argument('--ext-cov', required=True)
    parser.add_argument('--ext-label', required=True)
    parser.add_argument('--train-names', required=True)
    parser.add_argument('--out-prefix', required=True)
    args = parser.parse_args()

    # Load Data
    X_new, y_new, full_names, identifiers = utils.load_data_split(
        f"{args.ext_feature}_xgb.geno", args.ext_cov, f"{args.train_names}_xgb.names", args.ext_label
    )

    # Load Models
    print(f">>> Loading models from /ref/...")
    xgb_model = joblib.load(XGB_PATH)
    enet_model = joblib.load(ENET_PATH)

    # Predict
    print(">>> Running predictions...")
    # XGBoost
    xgb_probs = xgb_model.predict_proba(xgb.DMatrix(X_new))[:, 1]
    
    del X_new, y_new, full_names, identifiers

    # Elastic Net (using np.float32 for input, filling NA with median of each column)
    X_new, y_new, full_names, identifiers = utils.load_data_split(
        f"{args.ext_feature}_enet.geno", args.ext_cov, f"{args.train_names}_enet.names", args.ext_label
    )
    X_new.columns = full_names
    X_new = X_new.fillna(X_new.median())
    #If median filling still results in NA (e.g. when all values for a given variant is missing, replacing with REF 0/0 genotype)
    X_new = X_new.fillna(0)
    X_new_np = np.ascontiguousarray(X_new.values, dtype=np.float32)
    
    enet_probs = enet_model.predict_proba(X_new_np)[:, 1]

    # Create Output DataFrame
    results = identifiers.copy()
    results.columns = ['FID', 'IID']
    results['True_Label'] = y_new.values
    results['BD_mitoPRS_XGB'] = xgb_probs
    results['BD_mitoPRS_ENet'] = enet_probs

    # Loading other scores for appending
    csx_df = pd.read_csv(f"{args.out_prefix}.csx.profile", sep=r'\s+', usecols=['FID', 'IID', 'SCORE']).rename(columns={'SCORE': 'BD_mitoPRS_PRSCSx'})
    ice_df = pd.read_csv(f"{args.out_prefix}.all_score", sep=r'\s+', usecols=['FID', 'IID', 'Pt_0.25']).rename(columns={'Pt_0.25': 'BD_mitoPRS_PRSice'})
    pc_df = pd.read_csv(args.ext_cov, sep=r'\s+', usecols=['FID', 'IID', 'PC1', 'PC2', 'PC3', 'PC4', 'PC5'])

    # 7. Export
    out_file = os.path.join(output_dir, f"{args.out_prefix}_predictions.csv")
    results = results.merge(csx_df, on=['FID', 'IID'], how='left')
    results = results.merge(ice_df, on=['FID', 'IID'], how='left')
    results = results.merge(pc_df, on=['FID', 'IID'], how='left')
    results.to_csv(out_file, index=False)
    
if __name__ == "__main__":
    main()








