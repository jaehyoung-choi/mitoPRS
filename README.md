# mitoPRS
**Pipeline for calculation of mitoPRS for psychiatric disorders.**
## Description
The provided files compute calculate mitoPRS for psychiatric disorders.
Beta Version (Feb 2026)

Currently supported: Bipolar Disorder; ~~Schizophrenia~~ (updating soon)

The current version contains computation of ***mitoPRS*** (*genetic risk score for disorder based on single-nucleotide variations attributable to mitochondrially-acting protein coding genes*) using:
- PRSice-2
- PRS-CSx (auto, EUR reference)
- XGBoost
- Elastic Net Regression (L1L2 Regularized Regression)
- ~~Convolutional Neural Network~~ (updating soon)

The mitoPRS pipeline estimates ancestry-related principal components using 1000 Genome Project (phase3; GRChr37) as reference panel, using variants included in the Human Genome Diversity Project which are confidently genotyped within the discovery set from Psychiatric Genomics Consortium Core Datasets. The pipeline extracts genetic variations located within extended coding regions of MitoCarta 3.0, performs auto-thresholding based on pre-computed summary statistics, to calculate the mitoPRS using 5 different algorithms.

_Note: The majority of the development/discovery data is dependent on individuals of EUR-like Superpopulation Ancestry_

_Note: The script will automatically search for REF/ALT formats or strand-flips on variants to be used for scoring. If a variant is not found, or REF/ALT is different from the reference, or is tri-allelic, it will generate "dummy" variables as missing. The missing variables will be: [ignored for PRSice2 and PRSCSx], [Hanlded automatically in XGB], [Filled with REF/REF for OADP and ENET]_ 

### Contact
jaehyoung.choi@mail.utoronto.ca

### References
- FRAPOSA (https://github.com/PGScatalog/fraposa_pgsc)
- MitoCarta 3.0 (https://www.broadinstitute.org/mitocarta/mitocarta30-inventory-mammalian-mitochondrial-proteins-and-pathways)
- Psychiatric Genomics Consortium (https://pgc.unc.edu/)
- PRSice-2 (https://doi.org/10.1093/gigascience/giz082)
- PRS-CSx (https://doi.org/10.1038/s41588-022-01054-7)

**Reference to current work**: ***Choi et al. (Abstract: https://doi.org/10.1016/j.euroneuro.2024.08.316; publication in preparation)***

## Requirements
### Data
Input Data (Target): Plink binary files on ***GRCh37/hg19*** coordinates.
"TargetPrefix" refers to the file prefix of the plink binary files (E.g. *targetprefix*.{bim, bed, fam})

> Place target data in ./mitoPRS/ directory

Reference 1: 1KG Reference For PC-projection (Download from below)
> Place reference data in ./mitoPRS/ref/ directory

### VENV setting (tested)
Tested OS: Redhat Enterprise Linux Release 9.6 (Plow) and Ubuntu 24.04 LTS (Noble Numbat)

Key Requirements for are saved in ```mitoprs_requirements.txt```

> ```git clone https://github.com/jaehyoung-choi/mitoPRS.git```

> ```cd mitoPRS```

> ```conda create -n mitoprs python=3.11.3```

> ```conda activate mitoprs```

> ```pip install -r mitoprs_requirements.txt```

> ```chmod +x *.sh```

### Preinstallation Software
PLINK 2.0 (https://www.cog-genomics.org/plink/2.0/) Most Recent Version

PLINK 1.90b (https://www.cog-genomics.org/plink/) Most Recent Version

Python >= 3.11.3 (Lower versions have not been tested)
> Make sure python is executable as "python"

R >= 3.4.3
> Make sure RScript is executable as "Rscript" 

PRSice2 (https://github.com/choishingwan/PRSice?tab=readme-ov-file)
> Make sure PRSice2_linux.R and binary is in the directory "/mitoPRS/PRSice/"

## Outline & Usage
1. Download Reference Files (1000 Genomes, and relevant variants for Principal Components based on Human Genome Diversity Project variants) from here: 

> ```https://www.dropbox.com/scl/fo/xdecc3pthm1q129bc2rgm/AGJcVMJyxsVqtKwoXFMUmb4?rlkey=7m11qxftru8hq1k2dbdeunhok&st=yxehuuxc&dl=0``` 
>> Move the reference files to /mitoPRS/ref/ Folder

2. Go through Checklist

### Checklist
> > Check PLINK1.90b and PLINK2 paths have been updated in the ./score_mitoPRS.sh bash script file (E.g.) ```export PATH="$PATH:/home/plink1.9:/home/plink2"```

> > Check PRSice2 executable and binary are in the folder ~/mitoPRS/PRSice/ folder

> > Check the 1KG reference data has been downloaded, and added to ~/mitoPRS/ref/ folder

> > Check your PLINK Binary data has no missing sex code (1 or 2; Phenotype code can be missing)

> > Check python is executable using "python" in CLI (If it is runnable through "python3", change the bash script directly, or add as alias)

> > Check bash scripts are executable (e.g. ```chmod +x *.sh```)

3. Run MitoPRS Score

```./run_mitoPRS.sh "targetprefix" "outprefix"```

## Output
A .csv file written to /mitoPRS/output/ containing:
- IID
- FID
- Phenotype Value (1 = Control, 2 = Case, -9/0 = Missing)
- BD_mitoPRS_prsice2 (Score output from PRS-ice2; un-normalized)
- BD_mitoPRS_prscsx (Score output from plink --score; un-normalized)
- BD_mitoPRS_enet (Predicted probability [0, 1])
- BD_mitoPRS_xgb (Predicted probability [0, 1])
- BD_mitoPRS_null (Predicted probability based on Covariate-only Logistic Regression Model)
- PC 1-5 (First 5 PCs projected based on FRAPOSA-OADP)
  
## Usage
```./run_mitoPRS.sh "targetprefix" "outprefix"```

## Discovery Data
Individual-level datasets from Psychiatric Genomics Consortium
- Bipolar Disorder Working Group (wave3)
- Schizophrenia Disorder Working Group (wave3)
