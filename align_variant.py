import pandas as pd
import sys

def main():
    
    ref_pref, tgt_pref = sys.argv[1], sys.argv[2]

    ref = pd.read_csv(f"{ref_pref}.bim", sep="\s+", header=None, 
                     names=["chr", "id_ref", "cm", "pos", "a1", "a2"])
    tgt = pd.read_csv(f"{tgt_pref}.bim", sep="\s+", header=None, 
                     names=["chr", "id_tgt", "cm", "pos", "ta1", "ta2"])

    # 1. Coordinate Normalization
    ref['chr_n'] = ref['chr'].astype(str).str.replace('chr', '', case=False)
    tgt['chr_n'] = tgt['chr'].astype(str).str.replace('chr', '', case=False)
    ref['m_key'] = ref['chr_n'] + ":" + ref['pos'].astype(str)
    tgt['m_key'] = tgt['chr_n'] + ":" + tgt['pos'].astype(str)

    # 2. Identify Matches
    merged = pd.merge(ref, tgt, on="m_key")
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', '0': '0',
                  'a': 't', 'c': 'g', 'g': 'c', 't': 'a'}

    # We use dictionaries to prevent the "Double Flagging" you encountered
    # Key = Target ID
    final_keep = {}    # {tgt_id: ref_id}
    final_remove = set()
    final_flip = set()

    for _, row in merged.iterrows():
        r1, r2 = str(row['a1']).upper(), str(row['a2']).upper()
        t1, t2 = str(row['ta1']).upper(), str(row['ta2']).upper()
        tid, rid = row['id_tgt'], row['id_ref']
        ct1, ct2 = complement.get(t1, t1), complement.get(t2, t2)

        is_match = (r1 == t1 and r2 == t2) or (r1 == t2 and r2 == t1)
        is_flip = (r1 == ct1 and r2 == ct2) or (r1 == ct2 and r2 == ct1)

        if is_match:
            final_keep[tid] = rid
        elif is_flip:
            final_keep[tid] = rid
            final_flip.add(tid)
        else:
            # Case 1 & 3: If it fails once, it must be removed 
            # even if another record at this position matched.
            final_remove.add(tid)

    # --- THE CLEANUP STEP ---
    # If a variant is in remove, it cannot be in keep.
    # This prevents the "--exclude" priority from creating a 63-variant gap.
    actual_keep_tgt_ids = [tid for tid in final_keep if tid not in final_remove]
    actual_update_map = [[tid, final_keep[tid]] for tid in actual_keep_tgt_ids]
    actual_flip_ids = [tid for tid in final_flip if tid in actual_keep_tgt_ids]

    # --- THE MASTER DUMMY SET ---
    # DUMMY = Everything in Reference - (Actually Kept)
    kept_ref_ids = set([x[1] for x in actual_update_map])
    dummy_df = ref[~ref['id_ref'].isin(kept_ref_ids)].copy()

    # 3. Output
    pd.Series(actual_keep_tgt_ids).to_csv("keep.txt", index=False, header=False)
    pd.Series(list(final_remove)).to_csv("remove.txt", index=False, header=False)
    pd.Series(actual_flip_ids).to_csv("flip.txt", index=False, header=False)
    pd.DataFrame(actual_update_map).to_csv("update_ids.txt", sep="\t", index=False, header=False)
    
    dummy_df[['chr', 'id_ref', 'cm', 'pos', 'a1', 'a2']].to_csv(
        "dummy_template.bim", sep="\t", index=False, header=False)

    print(f"Stats: RefTotal={len(ref)} | Kept={len(actual_keep_tgt_ids)} | Dummy={len(dummy_df)}")
    print(f"Check sum: {len(actual_keep_tgt_ids) + len(dummy_df)} (Should match RefTotal)")

if __name__ == "__main__":
    main()