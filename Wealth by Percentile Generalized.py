import csv
from typing import List
import matplotlib.pyplot as plt
import collections
import math
from forex_python.converter import CurrencyRates


# ---------------- #


# whether or not the graph includes the top 1 percent in the graph (makes the rest of the graph visible!)
one_percent = False # True or False

# pick which country(ies) you want to view
country = 'China' # String

# what currency should the graph use
currency_used = 'Canada' # String

# if you want to compare an income
compare_income = True # True or False

# what income do you want to compare
income = 100000 # Int
 

# ---------------- #

codes = {}

# get dictionary of monetary country codes
monetary_codes = {}
with open('codes-all.csv') as csv_file:
    list = csv.reader(csv_file, delimiter=',') 
    for row in list:
        if row[5] == "":
            monetary_codes[row[0]] = (row[2], row[1])

# get dictionary of country names and codes for WID
with open('WID_countries.csv') as csv_file:
    WID_codes = csv.reader(csv_file, delimiter=',') 
    next(WID_codes)

    for row in WID_codes:

        if len(row[0]) == 2:
            if row[2] != "":
                monetary_code = monetary_codes[row[1].upper()][0]
                currency_name = monetary_codes[row[1].upper()][1]
                codes[row[1].upper()] = (row[0], monetary_code, currency_name)
            elif row[2] == "":
                codes[row[1].upper()] = (row[0], 'USD', 'United States Dollar')

        elif row[0][0] == 'U' and row[0][1] == 'S':
            codes[row[1].upper()] = (row[0], 'USD', 'United States Dollar')


# converts user input to upper case
country = country.upper()
currency_used = currency_used.upper()

# gets conversion rate
c = CurrencyRates()
conversion_rate = c.get_rate(codes[country][1], codes[currency_used][1])


# convert money into correct currency
def convert_money(conversion_rate, value):
    return float(value) * conversion_rate


# get and clean data    
def get_data(country):

    aptinc = {}

    # cleaning the data
    with open(f'country_data/WID_data_{codes[country][0]}.csv') as csv_file:
        data = csv.reader(csv_file, delimiter=';') 

        for row in data:

            # I only care about the year 2021 and the variable 'aptinc'
            if 'aptinc992' in row[1] and row[3] == '2021':

                # translates percentile string into a numerical value
                index = 0
                for i in row[2]:

                    # index 0 is always 'p', so we get rid of that
                    if index == 0:
                        row[2] = row[2][1:]

                    # each string has a p in the middle of the numbers we care about. I also only 
                    # care about the rows which measure a single percentile 
                    # (upper bound - lower bound <= 1)
                    elif i == 'p':
                        lb = float(row[2][:index - 1])
                        ub = float(row[2][index:])

                        # if the top one percent is being filtered out adds another requirement
                        if not one_percent:
                            if ub - lb <= 1 and ub <= 99: 
                                row[2] = ub
                            else: 
                                row[2] = 0
                        else:
                            if ub - lb <= 1:
                                row[2] = ub
                            else: row[2] = 0
                    index += 1

                # adds wanted, cleaned data to a dictionary. Also converts all values to one currency
                if row[2] != 0:                    
                    aptinc[row[2]] = convert_money(conversion_rate, row[4])

    return aptinc


# find the closest percentile to an income
def closest_percentile(income, data):
    closest = math.inf
    percentile = float()
    for i in data:
        difference = income - data[i]
        if abs(difference) < closest:
            closest = difference
            percentile = i
    return percentile


# ---------------- #


unsorted_data = {}
percentiles = []
average_income = []


# gets data for the country
data = get_data(country)
for i in data:
    unsorted_data[i] = data[i]


# sorts the data
sorted = collections.OrderedDict(sorted(unsorted_data.items()))
for i in sorted:
    percentiles.append(i)
    average_income.append(data[i])


# makes countries pretty for printing
country = country.lower()
country = country.capitalize()

# calculates where the income places against incomes from country(ies)
blurb = ""        
if compare_income:
    percentile = closest_percentile(income, sorted)
    blurb = f"You are richer than {round(percentile)} percent of {country}'s population"

# plot this data!
plt.plot(percentiles,average_income)
plt.title(f'{country} Average Annual Income by Percentile')
plt.xlabel(f'Percentile\n{blurb}')
plt.ylabel(f'Average Annual Income of {country}({codes[currency_used][1]})')
plt.axvline(x = 99, color = 'r', label = '99th percentile', linestyle=':')
if compare_income:
    plt.axvline(x = percentile, color = 'g', label = f'{income} {codes[currency_used][2]}')
plt.legend(bbox_to_anchor = (0, 1), loc = 'upper left')
plt.show()
