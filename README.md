# Cantera-ext
## New features in Version 4:
(a) 0_D extinction calculation speed is greatly increased.

(b) A calculator is added to calculate species LHV.

(c) NO and NO2 ppmvd at 15%O2 level is exported.
## Introduction

Cantera extension program is developed for Phoenix Biopower, Stockholm, Sweden.

Current version is for windows user only, if you need a version for Linux,

Email: Kai.Zhang.1@city.ac.uk

## Planned Works:

(a) Extra graphical grid towards calculation of single mixture chosen at interface.

(b) Throw error when users enter incorrect input.

(c) Report 1D solution at different residence time, rather than only at flame front.

(d) Group all needed libraries into one single executable package.

(e) CRN implementation

(f) Parallel calculation

(g) Add automatic plots for achieved datasets.


## Installation (assuming you have installed conda, refer to instruction)

Use the package manager [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html) to install Cantera-ext.

```bash
conda update --force conda
conda create -n cantera -c anaconda python=3.7
conda activate cantera
conda install --channel cantera/label/dev cantera
conda install -c anaconda numpy
conda install -c anaconda pandas
conda install -c anaconda xlrd
conda install -c anaconda openpyxl
```

## Usage

```bash
python V3.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
No License assigned yet. Any use of this program must obtained permission from Authors:
Kai.Zhang.1@city.ac.uk or duwig@mech.kth.se
