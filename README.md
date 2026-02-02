# mitoPRS
**Pipeline for calculation of mitoPRS for psychiatric disorders.**
## Description
The provided files compute calculate mitoPRS for psychiatric disorders.

Currently supported: Bipolar Disorder, Schizophrenia

The current version contains computation of mitoPRS (genetic risk score for disorder based on single-nucleotide variations attributable to mitochondrially-acting protein coding genes) using:
- PRSice-2
- PRS-CSx (auto, EUR reference)
- XGBoost
- ElasticNet (L1L2 Regression)
- Convolutional Neural Network

The mitoPRS pipeline estimates ancestry-related principal components using 1000 Genome Project (phase3; GRChr37) as reference panel, using variants included in the Human Genome Diversity Project which are confidently genotyped within the discovery set from Psychiatric Genomics Consortium. The pipeline extracts genetic variations located within extended regions of MitoCarta 3.0, performs auto-thresholding based on pre-computed summary statistics, to calculate the mitoPRS using 5 different algorithms.

_The majority of the development/discovery data is dependent on individuals of European Superpopulation Ancestry_

### References
- FRAPOSA (https://github.com/PGScatalog/fraposa_pgsc)
- MitoCarta 3.0 (https://www.broadinstitute.org/mitocarta/mitocarta30-inventory-mammalian-mitochondrial-proteins-and-pathways)
- Psychiatric Genomics Consortium (https://pgc.unc.edu/)

Reference: ***Choi et al. (In preparation)***

## Requirements
### Data
Input Data (Target): Plink binary files on GRCh37/hg19 coordinates.

Reference: datalink

### Preinstallation Software
PLINK 2.0 (https://www.cog-genomics.org/plink/2.0/)

Python >= 3.8.3

## Outline


## Usage

## Discovery Data
Psychiatric Genomics Consortium
- Bipolar Disorder Working Group (wave3)
- Schizophrenia Disorder Working Group (wave2)
