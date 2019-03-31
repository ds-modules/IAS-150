import pandas as pd
import numpy as np
from datascience import *
import math as m
import qgrid as q
import pandas as pd
from scipy.stats import chi2_contingency

master_list = ['Cuba',
 'El Salvador',
 'Guatemala',
 'Honduras',
 'Mexico',
 'Venezuela (Bolivarian Republic of)',
 'China',
 'India',
 'Philippines',
 'Viet Nam',
 'Afghanistan',
 'Iraq',
 'Pakistan',
 'Syrian Arab Republic',
 'Ethiopia',
 'Ghana',
 'Kenya',
 'Nigeria',
 'Somalia',
 'South Africa']
# select certain countries from table, either from origin or destination
def load_data_excel(filename):
    table = pd.read_excel(filename)
    table = table.loc[table['Code'] <900,:]
    table = table.replace('..', 0)
    table = table.drop(columns = ['Code','Notes'])
    return table

# select a region of countries as specified in the spec
def select_region(table, region_list, origin=False):
    if origin:
        return table.loc[:,['Year', 'Code', 'Country', 'Total'] + region_list]
    else:
        return table.loc[table['Country'].isin(region_list), :]

def array_summer2(array1, array2):
    new_lst = []
    for i in range(len(array1)):
            new_lst.append(array1[i] + array2[i])
    return new_lst

def array_summer3(array1, array2, array3):
    new_lst = []
    for i in range(len(array1)):
            new_lst.append(array1[i] + array2[i] + array3[i])
    return new_lst

def array_summer6(array1, array2, array3, array4, array5, array6):
    new_lst = []
    for i in range(len(array1)):
            new_lst.append(array1[i] + array2[i] + array3[i] + array4[i] + array5[i] + array6[i])
    return new_lst

# takes columns and adds them together
def column_grouper(table, title):
    first = table.column(0)
    second = table.column(1)
    new_table = Table().with_columns('Year', first, 'Country', second)
    new_table.append_column(title + ' Under 15 years old', array_summer3(table.column(2), table.column(3), table.column(4)))
    new_table.append_column(title + ' 15-19 years old', table.column(5))
    new_table.append_column(title + ' 20-29 years old', array_summer2(table.column(6), table.column(7)))
    new_table.append_column(title + ' 30-39 years old', array_summer2(table.column(8), table.column(9)))
    new_table.append_column(title + ' 40-49 years old', array_summer2(table.column(10), table.column(11)))
    new_table.append_column(title + ' 50 years old and older', array_summer6(table.column(12), table.column(13), table.column(14), table.column(15),table.column(16), table.column(17)))
    return new_table

def table_1():
    old_migrant = pd.read_excel("migrant_table.xlsx")
    migrant = select_region(old_migrant, master_list)
    codes = Table.from_df(migrant).column(2)
    migrant_np = Table.from_df(migrant).drop('Code')
    male_migrant = migrant_np.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    female_migrant = male_migrant.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    total_migrant = column_grouper(migrant_np, 'All migrants').to_df()
    male_migrant = column_grouper(male_migrant, 'Male').drop(0,1).to_df()
    female_migrant = column_grouper(female_migrant, 'Female').drop(0,1).to_df()
    pre_mig_table = pd.concat([total_migrant, male_migrant, female_migrant], axis=1)
    mig_table = Table.from_df(pre_mig_table).with_column('Code', codes).move_to_start('Code').move_to_start('Country').move_to_start('Year')
    return mig_table

def table_2():
    old_migrant = pd.read_excel("migrant_table.xlsx")
    migrant = select_region(old_migrant, master_list)
    codes = Table.from_df(migrant).column(2)
    table = load_data_excel("jordan_book_1.xlsx")
    table = select_region(table, master_list)
    table_np = Table().from_df(table)
    male_table = table_np.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    female_table = male_table.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    total_only = column_grouper(table_np, 'All migrants').to_df()
    male_only = column_grouper(male_table, 'Male').drop(0,1).to_df()
    female_only = column_grouper(female_table, 'Female').drop(0,1).to_df()
    pre_pop_table = pd.concat([total_only, male_only, female_only], axis=1)
    pop_table = Table.from_df(pre_pop_table).with_column('Code', codes).move_to_start('Code').move_to_start('Country').move_to_start('Year')
    return pop_table

# helper function to re-format table in case of tracking in-migrations
def columns_to_rows(table):

    country_original = table['Country'].iloc[0]
    country_list = list(table)[4:]
    year = table.iloc[0,0]
    code = table.iloc[0,1]
    first_country = country_list[0]

    new_df = pd.DataFrame({'Year': [year],'Code': [code],'Country of Origin': [first_country], 'Country of Destination: '+ country_original + ' (Counts)': table[first_country].iloc[0]})

    for country in country_list[1:]:
        new_df = new_df.append({'Year': year,'Code': code,'Country of Origin': country, 'Country of Destination: '+ country_original + ' (Counts)': table[country].iloc[0]}, ignore_index=True)

    return new_df

# gets total counts
def get_total(table,country,origin=False):
    if origin:
        total = table.loc[:,[country]].values.sum()
    else:
        total = table['Total'].values[0]
    return total

# get the top five origin/destination countries for a given country
def get_top_i(table, country, year, origin=False, i=5):

    if origin:
        table = table.loc[table['Year'] == year, :]
        table = table.loc[:,['Year', 'Code', 'Country', country]]

        # get total migration
        total = get_total(table,country,True)

        table = table.sort_values(by=[country], ascending=False)[0:i]
        table = table.rename(columns={'Country': 'Country of Destination', country: 'Country of Origin: ' + country + ' (Counts)'})
    else:
        table = table.loc[table['Year'] == year, :]
        table = table.loc[table['Country'] == country,:]

        total = get_total(table,country)

        table = columns_to_rows(table)
        table = table.sort_values(by=['Country of Destination: ' + country + ' (Counts)'], ascending=False)[0:i]

    return [table, total]

# converts to row
def table_to_row(table_list, country, origin=True):
    table = table_list[0]
    total = table_list[1]

    year = table.iloc[0,0]
    code = table.iloc[0,1]

    keys = ['Year',
        'Country',
        'Code',
        'Migration Type',
        'Total Migration',
       'Country 1',
       'Country 1 Count',
       'Country 2',
       'Country 2 Count',
       'Country 3',
       'Country 3 Count',
       'Country 4',
       'Country 4 Count',
       'Country 5',
       'Country 5 Count']

    if origin:
        dest_countries = table['Country of Destination'].values
        counts = table['Country of Origin: '+ country + ' (Counts)'].values

        dest_counts = []
        for i in range(len(dest_countries)):
            dest_counts.append(dest_countries[i])
            dest_counts.append(counts[i])

        values = [[i] for i in  [year, country, code, 'Emigration', total] + dest_counts]

        dictionary = dict(zip(keys, values))

    else:
        origin_countries = table['Country of Origin'].values
        counts = table['Country of Destination: '+ country + ' (Counts)'].values

        dest_counts = []
        for i in range(len(origin_countries)):
            dest_counts.append(origin_countries[i])
            dest_counts.append(counts[i])

        values = [[i] for i in  [year, country, code, 'Immigration', total] + dest_counts]

    return pd.DataFrame(dict(zip(keys, values)))

# concatenates 2 tables
def concatenate(table1, table2):
    lst = [table1, table2]
    temp = pd.concat([table1, table2], sort=True)
    return temp

#Retuns a table with one row of one country
def country_table(table, country):
    temp1 = pd.DataFrame()
    for year in table["Year"].unique():
        origin = get_top_i(table, country, year, origin=True, i=5)
        destination = get_top_i(table, country, year, origin=False, i=5)
        origin = table_to_row(origin, country, origin=True)
        destination = table_to_row(destination, country, origin=False)
        temp1 = concatenate(temp1, origin)
        temp1 = concatenate(temp1, destination)
    return temp1

# master table maker
def master(table):
    temp = pd.DataFrame()
    for country in master_list:
        print(country)
        new_table = country_table(table, country)
        temp = concatenate(temp, new_table)
    temp = temp[['Code',
        'Country',
        'Year',
        'Migration Type',
        'Total Migration',
       'Country 1',
       'Country 1 Count',
       'Country 2',
       'Country 2 Count',
       'Country 3',
       'Country 3 Count',
       'Country 4',
       'Country 4 Count',
       'Country 5',
       'Country 5 Count']]
    return temp
