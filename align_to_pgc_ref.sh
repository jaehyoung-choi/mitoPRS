#!/bin/bash

#Input: $1 Target Data, $2 Output Prefix, $3 Reference Prefix for BIM
#Output: PLINK-binary "OUT_PREFIX".{bed, bim, fam} 

export TGT_DATA="$1" #Target data prefix
export OUTPUT_PREFIX="$2" #Output file prefix
export REF_DATA="$3" #Reference data prefix

# 1. Logic via Python
python align_variants.py "$REF_DATA" "$TGT_DATA"

# 2. Process existing target variants
plink2 --bfile "$TGT_DATA" \
      --extract extract.txt \
      --flip flip.txt \
      --a1-allele force_a1.txt \
      --make-bed \
      --out tgt_intersect

# 3. Create dummy data for missing variants
# We use the target's FAM file so the sample IDs match perfectly
if [ -s missing_variants.bim.txt ]; then
    # Create a 0/0 (missing) PED file for these variants
    NUM_SAMPLES=$(wc -l < "${TGT_DATA}.fam")
    NUM_MISSING=$(wc -l < missing_variants.bim.txt)
    
    # Generate a dummy map file from the missing list
    awk '{print $1, $2, $3, $4}' missing_variants.bim.txt > dummy.map
    
    # Generate dummy ped file (FamilyID, SampleID, Paternal, Maternal, Sex, Phenotype, [0 0 for each SNP])
    # This creates a row for every sample with '0 0' for every missing SNP
    awk -v n=$NUM_MISSING '{printf "%s %s %s %s %s %s", $1, $2, $3, $4, $5, $6; for(i=1; i<=n; i++) printf " 0 0"; print ""}' "${TGT_DATA}.fam" > dummy.ped
    
    # Convert dummy to binary
    plink --ped dummy.ped --map dummy.map --make-bed --out tgt_missing --noweb
    
    # 4. Merge intersected data with missing data
    plink2 --bfile tgt_intersect --bmerge tgt_missing --make-bed --out tgt_combined
else
    cp tgt_intersect.bed tgt_combined.bed
    cp tgt_intersect.bim tgt_combined.bim
    cp tgt_intersect.fam tgt_combined.fam
fi

# 5. Final Recode
# Use --extract with final_order.txt to force the Reference order and include all SNPs
#plink --bfile tgt_combined \
#      --extract final_order.txt \
#      --make-bed --out "$OUTPUT_PREFIX"

# 6. Checking Variant order in reference
if diff <(awk '{print $4}' tgt_combined.bim) <(awk '{print $4}' "${REF_DATA}.bim") > /dev/null; then
      echo "Variant Order Checked: Positions are identically ordered. Proceeding ..."

      awk 'NR==FNR { col2[FNR]=$2; next } { $2 = col2[FNR]; print }' "${REF_DATA}.bim" tgt_combined.bim > "$OUTPUT_PREFIX".tmp
      mv "$OUTPUT_PREFIX".tmp tgt_combined.bim
      echo "Variant ID has been matched"

else
      echo "ERROR: Variant orders are different from $REF_DATA "
      exit 1
fi

plink2 --bfile tgt_combined \
       --extract "${REF_DATA}.bim" \
       --make-bed --out "$OUTPUT_PREFIX"

# Cleanup
rm extract.txt flip.txt force_a1.txt missing_variants.bim.txt final_order.txt
rm dummy.* tgt_intersect.* tgt_missing.* tgt_combined.*
rm *tmp*
