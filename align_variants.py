import pandas as pd
import sys

def main():
    ref_bfile = sys.argv[1]
    tgt_bfile = sys.argv[2]

    ref = pd.read_csv(f"{ref_bfile}.bim", sep="\s+", header=None,
                     names=["chr", "id", "cm", "pos", "a1", "a2"])
    tgt = pd.read_csv(f"{tgt_bfile}.bim", sep="\s+", header=None,
                     names=["chr", "id", "cm", "pos", "a1", "a2"])

    ref['coord'] = ref['chr'].astype(str) + ":" + ref['pos'].astype(str)
    tgt['coord'] = tgt['chr'].astype(str) + ":" + tgt['pos'].astype(str)

    # Intersection for alignment
    merged = pd.merge(ref, tgt, on="coord", suffixes=("_ref", "_tgt"))

    # Identify variants in Ref but NOT in Target
    missing_coords = set(ref['coord']) - set(tgt['coord'])
    ref_missing = ref[ref['coord'].isin(missing_coords)]

    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', '0': '0'}

    extract_list = []
    flip_list = []
    force_a1 = []

    # Process existing variants
    for _, row in merged.iterrows():
        r1, r2, t1, t2, tid = row['a1_ref'], row['a2_ref'], row['a1_tgt'], row['a2_tgt'], row['id_tgt']
        if (r1 == t1 and r2 == t2) or (r1 == t2 and r2 == t1):
            extract_list.append(tid)
            force_a1.append(f"{tid}\t{r1}")
        elif (r1 == complement.get(t1,t1) and r2 == complement.get(t2,t2)) or \
             (r1 == complement.get(t2,t2) and r2 == complement.get(t1,t1)):
            extract_list.append(tid)
            flip_list.append(tid)
            force_a1.append(f"{tid}\t{r1}")

    # Write files
    pd.Series(extract_list).to_csv("extract.txt", index=False, header=False)
    pd.Series(flip_list).to_csv("flip.txt", index=False, header=False)
    pd.DataFrame(force_a1).to_csv("force_a1.txt", sep="\t", index=False, header=False)

    # Create the "Missing" list for the Bash script to generate dummy variants
    # Format: Chr, ID, cM, Pos, A1, A2
    ref_missing[['chr', 'id', 'cm', 'pos', 'a1', 'a2']].to_csv("missing_variants.bim.txt",
                                                               sep="\t", index=False, header=False)

    # Order file for the very final step (using Reference IDs)
    ref['id'].to_csv("final_order.txt", index=False, header=False)

if __name__ == "__main__":
    main()
