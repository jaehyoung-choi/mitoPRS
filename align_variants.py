import pandas as pd
import sys

def get_agnostic_key(row, a1_col, a2_col):
    """
    Creates a key that is the same regardless of allele order or DNA strand.
    Example: A/G and T/C will both produce the same key.
    """
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', '0': '0'}
    
    # Get original pair and its complement
    p1 = sorted([str(row[a1_col]), str(row[a2_col])])
    p2 = sorted([complement.get(p1[0], p1[0]), complement.get(p1[1], p1[1])])
    
    # Use the alphabetically lower pair as the canonical version
    canonical_alleles = ":".join(min(p1, p2))
    return f"{row['chr']}:{row['pos']}:{canonical_alleles}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python align_logic.py <ref_prefix> <tgt_prefix>")
        sys.exit(1)

    ref_bfile, tgt_bfile = sys.argv[1], sys.argv[2]

    # Load BIM files
    ref = pd.read_csv(f"{ref_bfile}.bim", sep="\s+", header=None, 
                     names=["chr", "id", "cm", "pos", "a1", "a2"])
    tgt = pd.read_csv(f"{tgt_bfile}.bim", sep="\s+", header=None, 
                     names=["chr", "id", "cm", "pos", "a1", "a2"])

    # 1. Generate Strand-Agnostic Keys
    print("Generating strand-agnostic keys...")
    ref['key'] = ref.apply(lambda r: get_agnostic_key(r, 'a1', 'a2'), axis=1)
    tgt['key'] = tgt.apply(lambda r: get_agnostic_key(r, 'a1', 'a2'), axis=1)

    # 2. Map for Renaming (Unique 1:1 match)
    merged = pd.merge(ref, tgt, on="key", suffixes=("_ref", "_tgt"))
    
    # Create the ID update map: [Old_Target_ID, New_Ref_ID]
    update_ids = merged[['id_tgt', 'id_ref']]
    update_ids.to_csv("update_ids.txt", sep="\t", index=False, header=False)

    # 3. Identify Missing (Ref variants NOT in Target)
    missing_keys = set(ref['key']) - set(tgt['key'])
    ref_missing = ref[ref['key'].isin(missing_keys)]
    ref_missing[['chr', 'id', 'cm', 'pos', 'a1', 'a2']].to_csv(
        "missing_variants.bim.txt", sep="\t", index=False, header=False)

    # 4. Alignment Logic (Shared Variants)
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', '0': '0'}
    extract_list, flip_list = [], []

    for _, row in merged.iterrows():
        r1, r2 = row['a1_ref'], row['a2_ref']
        t1, t2 = row['a1_tgt'], row['a2_tgt']
        tid = row['id_tgt']
        
        # Scenario: Strand Flip Needed
        # If Reference (A/G) matches Target complement (T/C)
        is_flip = (r1 == complement.get(t1) and r2 == complement.get(t2)) or \
                  (r1 == complement.get(t2) and r2 == complement.get(t1))
        
        if is_flip:
            flip_list.append(tid)
        
        extract_list.append(tid)

    # Write PLINK control files
    pd.Series(extract_list).to_csv("extract.txt", index=False, header=False)
    pd.Series(flip_list).to_csv("flip.txt", index=False, header=False)
    
    # Master Reference info for final synchronization
    ref[['id', 'a1', 'a2']].to_csv("ref_alleles.txt", sep="\t", index=False, header=False)
    ref['id'].to_csv("final_order.txt", index=False, header=False)

    print(f"Done. Found {len(merged)} shared and {len(ref_missing)} missing variants.")

if __name__ == "__main__":
    main()