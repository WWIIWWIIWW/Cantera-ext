# Cantera-ext
# Cantera extension program developed for Phoenix Biopower, Stockholm, Sweden.
# The uploaded version 3 is for windows user only, if you need a version for Linux,
# Email: Kai.Zhang.1@city.ac.uk

# Refer to Instruction to know more about how to use this program.

Assuming you have installed conda in windows (refer to instruction):
Copy and past below commands to your conda terminal:
####################################################
conda update --force conda
conda create -n cantera -c anaconda python=3.7
conda activate cantera
conda install --channel cantera/label/dev cantera
conda install -c anaconda numpy
conda install -c anaconda pandas
conda install -c anaconda xlrd
conda install -c anaconda openpyxl
####################################################

Run the program with:
python V3.py
