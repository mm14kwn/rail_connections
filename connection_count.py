import numpy as np
import csv
import pickle
from selenium import webdriver
from itertools import compress
from os import path


def send_query(query_url, driver, debug=False):
    driver.get(query_url)
    source = driver.page_source
    # the format of this webpage is fairly fixed, so we can just search for the 'direct;' string
    if 'direct;' in source:
        nchange = 0

    elif 'change</a>' in source:
        nchange = 1

    elif 'changes</a>' in source:
        nchange = 2

    else:
        nchange = np.NaN


    if debug:
        print(query_url)
        print('nchange={0}'.format(nchange))
    return nchange


def count(destination='london',
          terminals=[
              'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG',
              'MYB', 'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT',
              'WAE'
          ],
          year=2019,
          month=2,
          day=12,
          hhmm=2359,
          arrdep='a',
          inputpath='/home/kinew/stations/',
          outputpath='/home/kinew/stations/results/',
          repeat_on_error=None,
          debug=False):

    date = '{0}-{1}-{2}'.format(year, month, day)
    time = '{0}'.format(hhmm) + arrdep
    # we need station codes to pass to the URL
    with open(path.join(inputpath, 'station_codes.csv')) as f:
        read_csv = csv.reader(f, delimiter=',')
        names = []
        codes = []
        for row in read_csv:
            names.append(row[0])
            codes.append(row[1])

    # strip headers
    names = names[1:]
    codes = codes[1:]

    # this was the easiest site to grab data off with the URL from 5m googling
    # network rail won't let me sign up for timetable data, so we have to use a website
    baseurl = 'https://traintimes.org.uk/{0}/{1}/{2}/{3}/changes=0'

    changes = np.NaN * np.ones(len(codes))

    # this should work with other webdrivers like Firefox, but phantomJS means no windows
    driver = webdriver.PhantomJS()
    logfile = open(path.join(outputpath, '{0}.log'.format(destination)), 'w')
    for count, code in enumerate(codes):
        if code in terminals:
            changes[count] = -1
        else:
            query_url = baseurl.format(code, destination, time, date)
            changes[count] = send_query(query_url, driver, debug=debug)
            if changes[count] > 1:
                nca = changes[count]
                query_url_dep = baseurl.format(code, destination, '0000d',
                                               date)
                ncd = send_query(query_url_dep, driver)
                changes[count] = np.nanmin([nca, ncd])
        if np.isnan(changes[count]):
            if repeat_on_error is not None:
                ind = 0
                datequery = '{0}-{1}-{2}'.format(year, month, day)
                while np.isnan(changes[count]) and ind < repeat_on_error:
                    query_url_arr = baseurl.format(code, destination, time,
                                                   datequery)
                    nca = send_query(query_url_arr, driver, debug=debug)
                    query_url_dep = baseurl.format(code, destination, '0000d',
                                                   datequery)
                    ncd = send_query(query_url_dep, driver, debug=debug)
                    changes[count] = np.nanmin([nca, ncd])
                    ind += 1
                    datequery = '{0}-{1}-{2}'.format(year, month, day + ind)
                    print(
                        'repeating {1} for the {0} time.'.format(ind, code),
                        end='\r')
            logfile.write(
                'No connection or Error parsing for Station code {0}, {1}\n'.
                format(codes[count], names[count]))
        elif changes[count] > 1:
            logfile.write(
                'More than 1 change for Station code {0}, {1}\n'.format(
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
    with open(
            path.join(outputpath,
                      '{0}_connections.pickle'.format(destination)),
            'wb') as f:
        pickle.dump(pdict, f)

    # calculate percentages
    ntotal = len(names) - len(terminals)
    ndirect = np.sum(changes == 0)
    nsingle = np.sum(changes == 1)
    nmore = np.sum(changes > 1)
    nnone = np.sum(np.isnan(changes))
    namesnone = compress(names, np.isnan(changes))
    codesnone = compress(codes, np.isnan(changes))
    namesgt1 = compress(names, changes > 1)
    codesgt1 = compress(codes, changes > 1)
    with open(
            path.join(outputpath, '{0}_results.log'.format(destination)),
            'w') as resfile:

        resfile.write(
            '{0} percent of stations ({1}) have direct services to {2}\n'.
            format(100 * ndirect / ntotal, ndirect, destination))
        resfile.write(
            '{0} percent of stations ({1}) have services to {2} with a single connection\n'
            .format(100 * nsingle / ntotal, nsingle, destination))
        resfile.write(
            '{0} percent of stations ({1}) have services to {2} with more than one connection\n'
            .format(100 * nmore / ntotal, nmore, destination))
        resfile.write('These stations are:\n')
        for name, code in zip(namesgt1, codesgt1):
            resfile.write('{0} ({1})\n'.format(name, code))
        resfile.write(
            '{0} percent of stations ({1}) have no services to {2} or returned an error\n'
            .format(100 * nnone / ntotal, nnone, destination))
        resfile.write('These stations are:\n')
        for name, code in zip(namesnone, codesnone):
            resfile.write('{0} ({1})\n'.format(name, code))

    # also can save as csv
    with open(
            path.join(outputpath, '{0}_connections.csv'.format(destination)),
            'w',
            newline='') as f:
        station_writer = csv.writer(f, delimiter=',')
        station_writer.writerow([
            'Name', 'Code',
            'Changes (-1 means terminus, 2 means 2+ changes, NaN means error or no connections possible)'
        ])
        for name, code, change in zip(names, codes, changes):
            station_writer.writerow([name, code, change])
