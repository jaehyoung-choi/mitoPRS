#!/bin/bash

## Input: $1-TargetPrefix $2-OutputPrefix
## Output: SCZ-MitoPRS output file in .csv

export target="$1"
export outpre="$2"

cd "$(dirname "$0")"

## Missing Variants will be replaced with ref allele from input REF/ALT format

./align_to_ref.sh "${target}" "${target}"_scz_mt "ref/combinedsczset" #$1=TargetPrefix $2=OutPrefix $3=reference bim prefix

#Make sure PRSice.R is located in ./PRSice/ directory
#Note summary statistic is already thresholded at p<0.42, and Clumped accordingly to the discovery data structure
Rscript PRSice/PRSice.R \
      --prsice PRSice/PRSice_linux \
      --base ref/SCZ.mitoPRS.sumstat.postCT.txt \
      --target "${target}"_scz_mt \
      -- \
      --binary-target T \
      --bar-levels 0.42 \
      --fastscore \
      --stat OR \
      --no-regress --no-clump --no-full \
      --out "$outpre"

plink --bfile "${target}"_scz_mt --score ref/PRSCSx.scz.combined.txt 2 4 6 --out "$outpre".scz.csx

# Extracting Variants for Model Input

plink --bfile "${target}"_scz_mt --extract ref/scz_xgb_varids.txt --keep-allele-order --recode A --out "$outpre"_scz_xgb

awk 'BEGIN {OFS="\t"} {print $1, $2, $3, $4, $5, $6}' "$outpre"_scz_xgb.raw > "$outpre".pheno
awk '{for(i=7;i<=NF;i++) printf $i (i==NF?ORS:OFS)}' "$outpre"_scz_xgb.raw | awk 'BEGIN {OFS="\t"} {$1=$1}1' > "$outpre"_scz_xgb.geno
sed -n '1p' "$outpre"_scz_xgb.geno > scz_varids_xgb.names
tail -n +2 "$outpre"_scz_xgb.geno > file.tmp && mv file.tmp "$outpre"_scz_xgb.geno
tail -n +2 "$outpre".pheno | awk '{$1=$1}1' OFS='\t' > file.tmp && mv file.tmp "$outpre".pheno

plink --bfile "${target}"_scz_mt --extract ref/scz_enet_varids.txt --keep-allele-order --recode A --out "$outpre"_scz_enet
awk '{for(i=7;i<=NF;i++) printf $i (i==NF?ORS:OFS)}' "$outpre"_scz_enet.raw | awk 'BEGIN {OFS="\t"} {$1=$1}1' > "$outpre"_scz_enet.geno
sed -n '1p' "$outpre"_scz_enet.geno > scz_varids_enet.names
tail -n +2 "$outpre"_scz_enet.geno > file.tmp && mv file.tmp "$outpre"_scz_enet.geno

python score_mitoprs_scz.py --ext-feature "${outpre}"_scz --ext-cov "${target}".oadp --ext-label "${outpre}".pheno --train-names "varids" --out-prefix "${outpre}"

#Cleanup for next scoring step
rm *.geno
rm *.pheno
rm varids*
rm *.profile
rm *.all_score
rm *.prsice
rm *.log
rm *_model.*
rm *_mt.*
rm *.raw
rm ancestry*
rm *.names
