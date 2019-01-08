import numpy as np
import csv
import pickle
from selenium import webdriver
from itertools import compress

# we need station codes to pass to the URL
with open('station_codes.csv') as f:
    read_csv = csv.reader(f, delimiter=',')
    names = []
    codes = []
    for row in read_csv:
        names.append(row[0])
        codes.append(row[1])

# London terminal status codes - we don't need journeys between these
terminals = [
    'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG', 'MYB',
    'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT', 'WAE'
]
# strip headers
names = names[1:]
codes = codes[1:]

# we can put in 'london' here for all terminals
destination='london'

# this was the easiest site to grab data off with the URL from 5m googling
# network rail won't let me sign up for timetable data, so we have to use a website
baseurl = 'https://traintimes.org.uk/{0}/{1}/2359a/2019-02-12/changes=0'

changes = np.NaN * np.ones(len(codes))

# this should work with other webdrivers like Firefox, but phantomJS means no windows
driver = webdriver.PhantomJS()
for count, code in enumerate(codes):
    if code in terminals:
        changes[count] = -1
    else:
        query_url = baseurl.format(code, destination)
        driver.get(query_url)
        source = driver.page_source
# the format of this webpage is fairly fixed, so we can just search for the 'direct;' string
        if 'direct;' in source:
            changes[count] = 0

        elif 'change</a>' in source:
            changes[count] = 1
    if np.isnan(changes[count]):
        print(
            'More than 1 change for Station code {0}, {1}                    \r'
            .format(codes[count], names[count]))
    elif changes[count] < 0:
        print('{0} ({1}) is a London Terminus!                 \r'.format(
            names[count], codes[count]))
    else:
        print(
            '{2} changes for Station code {0}, {1}                         \r'.
            format(codes[count], names[count], changes[count]))
print('')
# remember to quit the webdriver!
driver.quit()

# save as pickle
pdict = {}
pdict['names'] = names
pdict['codes'] = codes
pdict['changes'] = changes
with open('london_connections.pickle', 'wb') as f:
    pickle.dump(pdict, f)

# calculate percentages
ntotal = len(names) - len(terminals)
ndirect = np.sum(changes == 0)
nsingle = np.sum(changes == 1)
nmore = np.sum(np.isnan(changes))
namesgt1 = compress(names, np.isnan(changes))
codesgt1 = compress(codes, np.isnan(changes))

print('{0} percent of stations ({1}) have direct services to London'.format(
    100 * ndirect / ntotal, ndirect))
print(
    '{0} percent of stations ({1}) have services to London with a single connection'
    .format(100 * nsingle / ntotal, nsingle))
print(
    '{0} percent of stations ({1}) have services to London with more than one connection'
    .format(100 * nmore / ntotal, nmore))
print('These stations are:')
for name, code in zip(namesgt1, codesgt1):
    print('{0} ({1})'.format(name, code))

# also can save as csv
with open('london_connections.csv', 'w', newline='') as f:
    station_writer = csv.writer(f, delimiter=',')
    station_writer.writerow(
        ['Name', 'Code', 'Changes (-1 means terminus, NaN means 2+ changes)'])
    for name, code, change in zip(names, codes, changes):
        station_writer.writerow([name, code, change])

    
