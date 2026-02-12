# mitoPRS
**Pipeline for calculation of mitoPRS for psychiatric disorders.**
## Description
The provided files compute calculate mitoPRS for psychiatric disorders.

Currently supported: Bipolar Disorder, Schizophrenia

The current version contains computation of ***mitoPRS*** (*genetic risk score for disorder based on single-nucleotide variations attributable to mitochondrially-acting protein coding genes*) using:
- PRSice-2
- PRS-CSx (auto, EUR reference)
- XGBoost
- Elastic Net Regression (L1L2 Regularized Regression)
- Convolutional Neural Network

The mitoPRS pipeline estimates ancestry-related principal components using 1000 Genome Project (phase3; GRChr37) as reference panel, using variants included in the Human Genome Diversity Project which are confidently genotyped within the discovery set from Psychiatric Genomics Consortium Core Datasets. The pipeline extracts genetic variations located within extended coding regions of MitoCarta 3.0, performs auto-thresholding based on pre-computed summary statistics, to calculate the mitoPRS using 5 different algorithms.

_Note: The majority of the development/discovery data is dependent on individuals of EUR-like Superpopulation Ancestry_

### References
- FRAPOSA (https://github.com/PGScatalog/fraposa_pgsc)
- MitoCarta 3.0 (https://www.broadinstitute.org/mitocarta/mitocarta30-inventory-mammalian-mitochondrial-proteins-and-pathways)
- Psychiatric Genomics Consortium (https://pgc.unc.edu/)

Reference: ***Choi et al. (Abstract: https://doi.org/10.1016/j.euroneuro.2024.08.316; publication in preparation)***

## Requirements
### Data
Input Data (Target): Plink binary files on ***GRCh37/hg19*** coordinates.
"TargetPrefix" refers to the file prefix of the plink binary files (E.g. *targetprefix*.{bim, bed, fam})

> Current version supports "rsids" and/or "CHR:POS" format. Ref and Alt Allele formats are saved in files within /mitoPRS/ref/ directory)

Reference 1: 1KG Reference For PC-projection (Download from below)

Reference 2: References for MitoPRS calculation (Available in /mitoPRS/ref/ in various formats)

Key Requirements for are saved in ```mitoprs_requirements.txt```

### Preinstallation Software
PLINK 2.0 (https://www.cog-genomics.org/plink/2.0/)

PLINK 1.90b (https://www.cog-genomics.org/plink/)

Python >= 3.11.3 (Lower versions have not been tested)
> Make sure python is executable as "python"

R >= 3.4.3
> Make sure RScript is executable as "Rscript" 

PRSice2 (https://github.com/choishingwan/PRSice?tab=readme-ov-file)
> Make sure PRSice2_linux.R is in the directory "/mitoPRS/PRSice/"

## Outline & Usage
1. Download Reference Files (1000Genomes, and relevant variants for Principal Components based on Human Genome Diversity Project) from here: ```https://www.dropbox.com/scl/fo/xdecc3pthm1q129bc2rgm/AGJcVMJyxsVqtKwoXFMUmb4?rlkey=7m11qxftru8hq1k2dbdeunhok&st=yxehuuxc&dl=0``` --> Move the reference files to /mitoPRS/ref/ Folder

2. Set the PLINK executable paths in bash script (.sh) files.

E.g.
```
export PATH="$PATH:/home/plink1.9:/home/plink2"
```
   
3. Run MitoPRS Score

```./score_mitoPRS.sh "targetprefix"```

## Output
A .csv file containing the following:
- IID
- FID
- Within-family ID of Father
- Within-family ID of Mother
- Sex code (1 = male, 2 = female, 0 = Unknown)
- Phenotype Value (1 = Control, 2 = Case, -9/0 = Missing)
- BD_mitoPRS_prsice2 (Score output from PRS-ice2; un-normalized)
- BD_mitoPRS_prscsx (Score output from plink --score; un-normalized)
- BD_mitoPRS_enet (Predicted probability [0, 1])
- BD_mitoPRS_xgb (Predicted probability [0, 1])
- BD_mitoPRS_null (Predicted probability based on Covariate-only Logistic Regression Model)
- First 5 PCs projected based on FRAPOSA-OADP

## Usage
```./score_mitoPRS "targetprefix"```
## Discovery Data
Individual-level datasets from Psychiatric Genomics Consortium
- Bipolar Disorder Working Group (wave3)
- Schizophrenia Disorder Working Group (wave3)
