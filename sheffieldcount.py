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

# destination group status codes - we don't need journeys between these
terminals = ['SHF']
# strip headers
names = names[1:]
codes = codes[1:]

# we can put in 'birmingham' here for all in birmingham station group
destination = 'sheffield'

# this was the easiest site to grab data off with the URL from 5m googling
# network rail won't let me sign up for timetable data, so we have to use a website
baseurl = 'https://traintimes.org.uk/{0}/{1}/2359a/2019-02-12/changes=0'

changes = np.NaN * np.ones(len(codes))

# this should work with other webdrivers like Firefox, but phantomJS means no windows
driver = webdriver.PhantomJS()
logfile = open('{0}.log'.format(destination), 'w')
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
        logfile.write('More than 1 change for Station code {0}, {1}\n'.format(
            codes[count], names[count]))
    elif changes[count] < 0:
        logfile.write('{0} ({1}) is in the {2} station group!\n'.format(
            names[count], codes[count], destination))
    else:
        logfile.write('{2} changes for Station code {0}, {1}\n'.format(
            codes[count], names[count], changes[count]))

# remember to quit the webdriver and close logfile!
driver.quit()
logfile.close()
# save as pickle
pdict = {}
pdict['names'] = names
pdict['codes'] = codes
pdict['changes'] = changes
with open('{0}_connections.pickle'.format(destination), 'wb') as f:
    pickle.dump(pdict, f)

# calculate percentages
ntotal = len(names) - len(terminals)
ndirect = np.sum(changes == 0)
nsingle = np.sum(changes == 1)
nmore = np.sum(np.isnan(changes))
namesgt1 = compress(names, np.isnan(changes))
codesgt1 = compress(codes, np.isnan(changes))
with open('{0}_results.log'.format(destination), 'w') as resfile:

    resfile.write(
        '{0} percent of stations ({1}) have direct services to {2}\n'.format(
            100 * ndirect / ntotal, ndirect, destination))
    resfile.write(
        '{0} percent of stations ({1}) have services to {2] with a single connection\n'
        .format(100 * nsingle / ntotal, nsingle, destination))
    resfile.write(
        '{0} percent of stations ({1}) have services to {2} with more than one connection\n'
        .format(100 * nmore / ntotal, nmore, destination))
    resfile.write('These stations are:\n')
    for name, code in zip(namesgt1, codesgt1):
        resfile.write('{0} ({1})\n'.format(name, code))

# also can save as csv
with open('{0}_connections.csv'.format(destination), 'w', newline='') as f:
    station_writer = csv.writer(f, delimiter=',')
    station_writer.writerow(
        ['Name', 'Code', 'Changes (-1 means terminus, NaN means 2+ changes)'])
    for name, code, change in zip(names, codes, changes):
        station_writer.writerow([name, code, change])
