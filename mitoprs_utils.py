import os
import gc
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import RandomizedSearchCV, train_test_split, PredefinedSplit
from scipy.stats import uniform, randint, loguniform
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV

def load_data_split(feat_path, cov_path, name_path, label_path):
    """Loads a specific split independently using memory-efficient dtypes."""
    names_df = pd.read_csv(name_path, sep=r'\s+', header = None, engine = 'python')
    feature_names = names_df.iloc[0].values.tolist()
    X_main = pd.read_csv(feat_path, sep='\t', header=None,
                         engine='c', low_memory=False, memory_map=True, na_values=['-9','NA', '3'])

    print(f"Checking shapes of loaded data: {X_main.shape}, feature length: {len(feature_names)}")

    print(f"Data loaded with shape: {X_main.shape}")
    if len(feature_names) == X_main.shape[1]:
        X_main.columns = feature_names
    else:
        print(f"Warning: Name count ({len(feature_names)}) does not match. Column count ({X_main.shape[1]}).")
        
    cov_df = pd.read_csv(cov_path, sep='\t').iloc[:, 2:]
    cov_names = [f"Covariate{i+1}" for i in range(cov_df.shape[1])]
    cov_df.columns = cov_names

    label_df = pd.read_csv(label_path, sep='\t', header=None)
    print(label_df.shape)
    print(X_main.shape)

    # Binary encoding: 2 is 1 (Case), 1 is 0 (Control)
    sex = (label_df.iloc[:, 4] == 2).astype(np.int8)
    y = (label_df.iloc[:, 5] == 2).astype(np.int8)
    id_df = label_df.iloc[:, 0:2]

    X_main.reset_index(drop=True, inplace=True)
    cov_df.reset_index(drop=True, inplace=True)

    X = pd.concat([X_main, cov_df], axis=1)
    X = X.copy()
    X['sex'] = sex.values
    print(np.isinf(X).sum().sum())
    print(f"Final dimension of dataset {X.shape}")
    print(f"Label breakdown: {np.unique(y, return_counts=True)}")

    # --- Feature Matrix Integrity Check ---
    print("\n[Integrity Check] Checking Feature Matrix X...")

# 1. Check for NaNs
    nan_count = X.isna().sum().sum()
    if nan_count > 0:
        print(f"⚠️  WARNING: Found {nan_count} NaN values. XGBoost will handle them, but ensure this is expected.")

# 2. Check for Infinite values (The likely cause of NaN scores)
    inf_count = np.isinf(X.values).sum()
    if inf_count > 0:
        print(f"❌ CRITICAL: Found {inf_count} infinite values! Replacing with NaNs...")
        X = X.replace([np.inf, -np.inf], np.nan)

# 3. Check for Constant Columns (Zero Variance)
# These columns provide no information and can sometimes slow down training
    constant_cols = [col for col in X.columns if X[col].nunique() <= 1]
    if len(constant_cols) > 0:
        print(f"ℹ️  Note: Found {len(constant_cols)} columns with zero variance (constant values).")

    print(f"[Integrity Check] Final Matrix Shape: {X.shape}\n")
    
    full_names = X.columns.tolist()

    del X_main
    del cov_df
    gc.collect()

    return X, y, full_names, id_df

class InformedElasticNet(LogisticRegression):
    def __init__(self, C=1.0, l1_ratio=0.5, max_iter=3000, tol=0.01, betas=None):
        self.betas = betas  # This will be preserved during cloning
        self.tol = tol
        super().__init__(
            penalty='elasticnet',
            solver='saga',
            C=C,
            l1_ratio=l1_ratio,
            max_iter=max_iter,
            warm_start=True, # Necessary for injection
            tol=self.tol,
            n_jobs=-1
        )

    def fit(self, X, y):
        # Designed to use the effect sizes of the input features from summary statistics as initial coefficients for training.
        # In this case, the ENET coverges faster, and higher tolerance can be used for speeding up training without sacrificing much performance.
        # 1. Initialize internal state (fitting on random 1000 samples to set up the coefficient structure)
        rng = np.random.default_rng(seed=42)
        idx = rng.choice(25000, size = 1000, replace = False)
        X_init = X.iloc[idx] if hasattr(X, 'iloc') else X[idx]
        y_init = y.iloc[idx] if hasattr(y, 'iloc') else y[idx]
        print(f"Fitting Initial Subset to set coefficients")
        super().fit(X_init, y_init)
        # 2. Inject betas if they exist (this was input as betas from sumstat file for variants, and also for covariate-only LR model)
        if self.betas is not None:
            # Ensure betas match feature count of X
            self.coef_ = self.betas.astype(np.float64)
            
        # 3. Resume training on full data
        return super().fit(X, y)





