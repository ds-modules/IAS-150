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
    return country_code_year(mig_table)

def table_2():
    old_migrant = pd.read_excel("migrant_table.xlsx")
    migrant = select_region(old_migrant, master_list)
    codes = Table.from_df(migrant).column(2)
    table = load_data_excel("jordan_book_1.xlsx")
    table = select_region(table, master_list)
    table_np = Table().from_df(table)
    male_table = table_np.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    female_table = male_table.drop(2,3,4,5,6,7,8).drop(2,3,4,5,6,7,8).drop(2,3,4)
    total_only = column_grouper(table_np, 'Total').to_df()
    male_only = column_grouper(male_table, 'Male').drop(0,1).to_df()
    female_only = column_grouper(female_table, 'Female').drop(0,1).to_df()
    pre_pop_table = pd.concat([total_only, male_only, female_only], axis=1)
    pop_table = Table.from_df(pre_pop_table).with_column('Code', codes).move_to_start('Code').move_to_start('Country').move_to_start('Year')
    return country_code_year(pop_table)

def country_code_year(table):
    table.move_to_start('Code')
    table.move_to_start('Country')
    table.sort('Country')
    rtn_table = Table()
    ethiopia_table = table.where('Country', 'Ethiopia').sort('Year')
    rtn_table = ethiopia_table
    for country in master_list:
        if country is 'Ethiopia':
            continue
        else :
            country_table = table.where('Country', country).sort('Year')
            rtn_table.append(country_table)
    return rtn_table