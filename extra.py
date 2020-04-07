import pandas as pd
import csv
def dry_data_reader(data_name):
    print ("*************")
    print ("Starting dry based calculation!")
    data = pd.read_excel(data_name, header=0, keep_default_na = False)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    fuel_data = data.loc[:, data.columns != 'ER']
    fuel_data_no_steam = fuel_data.loc[:, fuel_data.columns != 'H2O']

    fuel_data = fuel_data_no_steam.multiply((1 - fuel_data[["H2O"]].values), axis="index")
    fuel_data['H2O'] = data.loc[:, data.columns == 'H2O']
    ER = data['ER']
    #print (ER.values)

    fuel_keys = fuel_data.keys()
    #print (fuel_keys)

    fuel_list = [] ##list to store fuel_list = {'CH4':0.2, 'H2':0.8}
    for i in range(len(fuel_data.index)):
        fuel_dicts = {}
        for j in fuel_keys:
            fuel_dicts[j] = fuel_data.loc[i,j]
        fuel_list.append(fuel_dicts)
    return fuel_list, ER, data, fuel_data

def wet_data_reader(data_name):
    print ("*************")
    print ("Starting wet based calculation!")
    data = pd.read_excel(data_name, header=0, keep_default_na = False)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    fuel_data = data.loc[:, data.columns != 'ER']
    ER = data['ER']
    #print (ER.values)

    fuel_keys = fuel_data.keys()
    #print (fuel_keys)

    fuel_list = [] ##list to store fuel_list = {'CH4':0.2, 'H2':0.8}
    for i in range(len(fuel_data.index)):
        fuel_dicts = {}
        for j in fuel_keys:
            fuel_dicts[j] = fuel_data.loc[i,j]
        fuel_list.append(fuel_dicts)
    return fuel_list, ER, data, fuel_data

def write(data, csv_file, excel_file, header, solution):
    #Export result
    with open(csv_file, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        for i in range(len(data)):
            writer.writerow(solution[i])
    #Convert from csv to excel
    if input('csv output done! Convert to excel? [yes/no)] ') == 'yes':

        read_file = pd.read_csv (csv_file)
        read_file.to_excel (excel_file, index = None, header=True)
        print ('xlsx output done!')
    else:
        print ('csv output done!')
