import pandas as pd
import numpy as np

master_list = ['Cuba',
 'El Salvador',
 'Guatemala',
 'Honduras',
 'Mexico',
 'Venezuela (Bolivarian Republic of)',
 'China',
 'India',
 'Philippines',
 'Vietnam',
 'Afghanistan',
 'Iraq',
 'Pakistan',
 'Syria',
 'Ethiopia',
 'Ghana',
 'Kenya',
 'Nigeria',
 'Somalia',
 'South Africa']
# select certain countries from table, either from origin or destination
def load_data_excel(filename):
    table = pd.read_excel(filename)
    table = table.loc[table['Code.1'] <900,:]
    table = table.drop(columns=['Code.1', 'Other North', 'Other South'])
    table = table.replace('..', 0)
    return table

# select a region of countries as specified in the spec
def select_region(table, region_list, origin=False):
    if origin:
        return table.loc[:,['Year', 'Code', 'Country', 'Total'] + region_list]
    else:
        return table.loc[table['Country'].isin(region_list), :]

# helper function to re-format table in case of tracking in-migration
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

# get the top five origin/destination countries for a given country
def get_top_i(table, country, year, origin=False, i=5):
    if origin:
        table = table.loc[table['Year'] == year, :]
        table = table.loc[:,['Year', 'Code', 'Country', country]]
        table = table.sort_values(by=[country], ascending=False)[0:i]
        table = table.rename(columns={'Country': 'Country of Destination', country: 'Country of Origin: ' + country + ' (Counts)'})
    else:
        table = table.loc[table['Year'] == year, :]
        table = table.loc[table['Country'] == country,:]
        table = columns_to_rows(table)
        table = table.sort_values(by=['Country of Destination: ' + country + ' (Counts)'], ascending=False)[0:i]
    return table


def table_to_row(table, country, origin=True):
    year = table.iloc[0,0]
    code = table.iloc[0,1]

    keys = ['Year',
        'Country',
        'Code',
        'Migration Type',
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

        values = [[i] for i in  [year, country, code, 'Emigration'] + dest_counts]

        dictionary = dict(zip(keys, values))

    else:
        origin_countries = table['Country of Origin'].values
        counts = table['Country of Destination: '+ country + ' (Counts)'].values

        dest_counts = []
        for i in range(len(origin_countries)):
            dest_counts.append(origin_countries[i])
            dest_counts.append(counts[i])

        values = [[i] for i in  [year, country, code, 'Immigration'] + dest_counts]

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
        origin = mf.get_top_i(table, country, year, origin=True, i=5)
        destination = mf.get_top_i(table, country, year, origin=False, i=5)
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
