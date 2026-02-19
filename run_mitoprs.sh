#!/bin/bash

## Input: $1-TargetPrefix $2-OutputPrefix
## Output: BD-MitoPRS output file in .csv

export target="$1"
export outpre="$2"

export PATH="$PATH:$HOME/plink1.9/:$HOME/plink2/"

cd "$(dirname "$0")"

## Extracting relevant variants to project PCs using FRAPOSA;
## Missing Variants will be replaced with ref allele from input REF/ALT format

./align_to_ref.sh "${target}" "ancestry" "ref/1kgref.bip" #use target, outputprefix, reference bim prefix as arguments
plink2 --bfile ancestry --extract ref/common_vars_bip.txt --fill-missing-with-ref --make-bed --out "${target}"_tmp #Re-organizing order of variants, forcing to ref of population
plink2 --bfile "${target}"_tmp --ref-allele ref/1kgref.bip.bim 6 2 --alt-allele ref/1kgref.bip.bim 5 2 --make-bed --out "${target}"_common #Forcing 1KG REF/ALT format

python -m FRAPOSA.fraposa_runner --stu_filepref "$target"_common --dim_ref 5 --dim_online 20 --out "${target}" ref/1kgref.bip

mv "${target}".pcs "${target}".oadp

## File Cleanup
rm -r "${target}"_tmp*
rm -r "${target}"_common*

./align_to_ref.sh "${target}" "${target}"_mt "ref/combinedbdset" #$1=TargetPrefix $2=OutPrefix $3=reference bim prefix

#Make sure PRSice.R is located in ./PRSice/ directory
#Note summary statistic is already thresholded at p<0.2, and Clumped accordingly to the discovery data structure
Rscript PRSice/PRSice.R \
      --prsice PRSice/PRSice_linux \
      --base ref/BD.mitoPRS.sumstat.postCT.txt \
      --target "${target}"_mt \
      --binary-target T \
      --bar-levels 0.25 \
      --fastscore \
      --stat OR \
      --no-regress --no-clump --no-full \
      --out "$outpre"

plink --bfile "${target}"_mt --score ref/PRSCSx.bip.combined.txt 2 4 6 --out "$outpre".csx

# Extracting Variants for Model Input

./align_to_ref.sh "${target}" "${target}"_model "ref/bd.allele.reference" 

plink --bfile "${target}"_model --extract ref/xgb_varids.txt --keep-allele-order --recode A --out "$outpre"_xgb

awk 'BEGIN {OFS="\t"} {print $1, $2, $3, $4, $5, $6}' "$outpre"_xgb.raw > "$outpre".pheno
awk '{for(i=7;i<=NF;i++) printf $i (i==NF?ORS:OFS)}' "$outpre"_xgb.raw | awk 'BEGIN {OFS="\t"} {$1=$1}1' > "$outpre"_xgb.geno
sed -n '1p' "$outpre"_xgb.geno > varids_xgb.names
tail -n +2 "$outpre"_xgb.geno > file.tmp && mv file.tmp "$outpre"_xgb.geno
tail -n +2 "$outpre".pheno | awk '{$1=$1}1' OFS='\t' > file.tmp && mv file.tmp "$outpre".pheno

plink --bfile "${target}"_model --extract ref/enet_varids.txt --keep-allele-order --recode A --out "$outpre"_enet
awk '{for(i=7;i<=NF;i++) printf $i (i==NF?ORS:OFS)}' "$outpre"_enet.raw | awk 'BEGIN {OFS="\t"} {$1=$1}1' > "$outpre"_enet.geno
sed -n '1p' "$outpre"_enet.geno > varids_enet.names
tail -n +2 "$outpre"_enet.geno > file.tmp && mv file.tmp "$outpre"_enet.geno

python score_mitoprs.py --ext-feature "${outpre}" --ext-cov "${target}".oadp --ext-label "${outpre}".pheno --train-names "varids" --out-prefix "${outpre}"

#Final Cleanup
rm *.geno
rm *.pheno
rm varids*
rm *.profile
rm *.png
rm *.all_score
rm *.prsice
rm *.valid
rm *.log
rm *_model.*
rm *_mt.*
rm *.raw
rm ancestry*




