#!/bin/bash

# Environment Variables
export TGT_DATA="$1"      
export OUTPUT_PREFIX="$2" 
export REF_DATA="$3"      

# 1. Coordinate Filter (PLINK2)
awk '{print $1, $4, $4, $2}' "${REF_DATA}.bim" > ref_ranges.txt
plink2 --bfile "$TGT_DATA" --extract range ref_ranges.txt --set-all-var-ids @:#:\$r:\$a --make-bed --out tgt_tmp_filtered

# 2. Logic via Python
python align_variant.py "$REF_DATA" tgt_tmp_filtered

# 3. Rename and Prune (PLINK2)
plink2 --bfile tgt_tmp_filtered --extract keep.txt --exclude remove.txt --make-bed --out tgt_tmp_sub
plink2 --bfile tgt_tmp_sub --update-name update_ids.txt --make-bed --out tgt_tmp_renamed

# 4. Correct Strand and Force Alleles (PLINK2)
# Here we use the BIM direct-reference for the first time
plink2 --bfile tgt_tmp_renamed \
       --flip flip.txt \
       --ref-allele "${REF_DATA}.bim" 6 2 \
       --alt-allele "${REF_DATA}.bim" 5 2 \
       --make-bed --out tgt_tmp_ref_set

# 5. Generate Dummy Binary (PLINK2 + PLINK 1.9)
if [ -s dummy_template.bim ]; then
    NUM_DUMMY=$(wc -l < dummy_template.bim)
    awk '{print $1, $2, $3, $4}' dummy_template.bim > dummy.map
    
    # Generate PED (All 0 0)
    cat tgt_tmp_ref_set.fam | tr -d '\r' | awk -v n=$NUM_DUMMY '{
        printf "%s %s %s %s %s %s", $1, $2, $3, $4, $5, $6; 
        for(i=1; i<=n; i++) printf " 0 0"; 
        print ""
    }' > dummy.ped

    plink2 --ped dummy.ped --map dummy.map --make-bed --out tgt_tmp_dummy
    
    # Force Dummy BIM to match Reference metadata exactly
    cp dummy_template.bim tgt_tmp_dummy.bim

    # Use PLINK 1.9 for the Binary Merge
    plink --bfile tgt_tmp_ref_set --bmerge tgt_tmp_dummy --make-bed --out tgt_tmp_merged
else
    mv tgt_tmp_ref_set.bed tgt_tmp_merged.bed
    mv tgt_tmp_ref_set.bim tgt_tmp_merged.bim
    mv tgt_tmp_ref_set.fam tgt_tmp_merged.fam
fi

# 6. Final Sync (PLINK2)
# Strictly match Reference variants, order, and REF/ALT structure

plink2 --bfile tgt_tmp_merged \
       --extract "${REF_DATA}.bim" \
       --ref-allele "${REF_DATA}.bim" 6 2 \
       --alt-allele "${REF_DATA}.bim" 5 2 \
       --make-bed \
       --out "$OUTPUT_PREFIX"

# Cleanup
rm tgt_tmp_* keep.txt flip.txt remove.txt update_ids.txt dummy_template.bim dummy.map dummy.ped ref_ranges.txt
