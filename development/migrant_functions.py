import pandas as pd
import numpy as np
import jordan as j
import random

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
    table = table.drop(columns=['Other North', 'Other South'])
    table = table.replace('..', 0)
    return table

# select a region of countries as specified in the spec
def select_region(table, region_list, origin=False):
    if origin:
        return table.loc[:,['Year', 'Code', 'Country', 'Total'] + region_list]
    else:
        return table.loc[table['Country'].isin(region_list), :]

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

# converts jordan's table to correct format
def jordan_columns_to_rows(jordan):
    keys = ['Country', 'Code', 'Year', 'Migration Type', 'Gender',
                                      'Migrants Under 15 years old',
                                     'Migrants 20-29 years old',
                                     'Migrants 30-39 years old',
                                     'Migrants 40-49 years old',
                                     'Migrants 50 years old and older']
    new_table = pd.DataFrame(columns=keys)

    for i in range(0, jordan.shape[0]):
        row = list(jordan.loc[[i]].values[0])
        predicates = row[0:3]

        total = row[3:9]
        male = row[9:15]
        female = row[15:21]

        female_new = predicates + ['Immigration', 'female'] +  female
        total_new = predicates + ['Immigration', 'total'] + total
        male_new = predicates + ['Immigration', 'male'] + male

        new_table = new_table.append(dict(zip(keys, female_new)), ignore_index = True)
        new_table = new_table.append(dict(zip(keys, male_new)), ignore_index = True)
        new_table = new_table.append(dict(zip(keys, total_new)), ignore_index = True)

    return new_table
