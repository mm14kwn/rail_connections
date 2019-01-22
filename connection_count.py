import numpy as np
import csv
import pickle
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from itertools import compress
from os import path
from selenium.common.exceptions import TimeoutException
import time


def send_queryTTO(query_url,
                  driver,
                  debug=False,
                  timeout=10,
                  ntries=10,
                  twait=20):
    driver.set_page_load_timeout(timeout)
    itries = 0
    nchange = np.NaN
    while itries < ntries:
        if np.mod(itries, 2) == 1:
            time.sleep(twait)
        try:
            driver.get(query_url)
            source = driver.page_source
            # the format of this webpage is fairly fixed, so we can just search for the 'direct;' string
            if 'direct;' in source:
                nchange = 0

            elif 'change</a>' in source:
                nchange = 1

            elif 'changes</a>' in source:
                nchange = 2
        except TimeoutException:
            itries += 1
            print('timed out for the {0} time'.format(itries), end='\r')
            print('', end='\r')
            continue
        break

    if debug:
        print(query_url)
        print('nchange={0}'.format(nchange))
    return nchange


def farequery(origin,
              destination,
              faretypes=['ANYTIME S', 'ANYTIME DAY S', 'ADVANCE'],
              routecodes=[0],
              debug=False):
    import requests
    import json
    from dictquery import DictQuery as DQ
    try:
        fare_url = 'http://api.brfares.com/querysimple?orig={0}&dest={1}'.format(
            origin, destination)
        request = requests.get(fare_url)
        faresdict = json.loads(request.text)
        findices = []
        for ind, ft in enumerate(faretypes):
            findices = [
                i
                for i, e in enumerate(DQ(faresdict).get('fares/ticket/name'))
                if e == ft
            ]
            if len(findices) > 0:
                ftype = faretypes[ind]
                break
            else:
                ftype = 'no route found'
        if debug:
            print('findices=')
            print(findices)
        for rc in routecodes:
            findex = [
                i for i in findices
                if DQ(faresdict).get('fares/route/code')[i] == rc
            ]
            if debug:
                print('findex=')
                print(findex)

            if len(findex) > 0:
                rcode = rc
                fare = np.min([
                    DQ(faresdict).get('fares/adult/fare')[f] / 100
                    for f in findex
                ])
                company = DQ(faresdict).get('fares/fare_setter/name')[
                    np.argmin([
                        DQ(faresdict).get('fares/adult/fare')[f]
                        for f in findex
                    ])]
                return fare, company, ftype, rcode
        fare = np.min(
            [DQ(faresdict).get('fares/adult/fare')[f] / 100 for f in findices])
        company = DQ(faresdict).get('fares/fare_setter/name')[np.argmin(
            [DQ(faresdict).get('fares/adult/fare')[f] for f in findices])]
        rcode = DQ(faresdict).get('fares/route/code')[np.argmin(
            [DQ(faresdict).get('fares/adult/fare')[f] for f in findices])]

    except (ValueError, json.decoder.JSONDecodeError):
        fare = np.NaN
        company = 'N/A'
        rcode = -998
        ftype = 'no route found'
    except requests.exceptions.RequestException as e:
        fare = np.NaN
        company = 'N/A'
        rcode = -997
        ftype = 'connection error: {0}'.format(e)
    return fare, company, ftype, rcode


def send_queryNRE(query_url,
                  driver,
                  dcap={},
                  debug=False,
                  timeout=20,
                  ntries=100,
                  twait=60):
    import re
    driver.set_page_load_timeout(timeout)
    itries = 0
    nchange = np.NaN
    jtime = np.NaN
    # minp = np.NaN
    # maxp = np.NaN
    # meanp = np.NaN
    while itries < ntries:
        if np.mod(itries, 3) == 1:
            time.sleep(twait)
        if np.mod(itries, 10) == 5:
            driver.close()
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
            driver.set_page_load_timeout(timeout)

        try:
            driver.get(query_url)
            source = driver.page_source
            chgpattern = r'\d\s+change'
            hhmmpattern = r'\d+?h \d+?m'
            # pricepattern = r'£\d+\.\d+'
            chgmatches = re.findall(chgpattern, source)
            hhmmmatches = re.findall(hhmmpattern, source)
            # pricematches = re.findall(pricepattern, source)
            if len(chgmatches) > 0:
                chg = [int(chgstr[0]) for chgstr in chgmatches]
                nchange = np.min(chg)
                nind = np.argmin(chg)
                hhmm = re.findall(r'\d+', hhmmmatches[nind])
                # prices = [float(p[1:]) for p in pricematches]
                # if len(prices) > 0:
                #     minp = np.min(prices)
                #     maxp = np.max(prices)
                #     meanp = np.mean(prices)
                hh = int(hhmm[0])
                mm = int(hhmm[1])
                jtime = mm + 60 * hh
        except TimeoutException:
            itries += 1
            print('timed out for the {0} time'.format(itries), end='\r')
            print('', end='\r')
            continue
        break


#     # the format of this webpage is fairly fixed, so we can just search for the strings
#     if '0 change' in source:
#         nchange = 0

#     elif '1 change' in source:
#         nchange = 1

#     elif '2 change' in source:
#         nchange = 2
# 3
#     else:
#         nchange = np.NaN

    if debug:
        print(query_url)
        print('nchange={0}'.format(nchange))
    return nchange, jtime, driver


def count(
        destination='london',
        terminals=[
            'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG',
            'MYB', 'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT',
            'WAE'
        ],
        year=19,
        month=2,
        day=12,
        hhmm=2359,
        arrdep='arr',
        inputpath='/home/kinew/stations/',
        outputpath='/home/kinew/stations/results/',
        repeat_on_error=None,
        debug=False,
        user_agent='Mozilla/5.0 (Linux; Android9; ONEPLUS A6013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.64 Mobile Safari/537.36'
):

    # date = '{0}-{1}-{2}'.format(year, month, day)
    # time = '{0}'.format(hhmm) + arrdep
    date = '{0:02d}{1:02d}{2}'.format(day, month, year)
    time = hhmm
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap['phantomjs.page.settings.userAgent'] = user_agent
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
    #    baseurl = 'https://traintimes.org.uk/{0}/{1}/{2}/{3}/changes=0'
    # developer requested not to use this website, reprogrammed for mobile NRE
    baseurl = 'http://m.nationalrail.co.uk/pj/plan/{0}/{1}/{2}/{3}/{4}'
    changes = np.NaN * np.ones(len(codes))
    jtime = np.NaN * np.ones(len(codes))
    fares = np.NaN * np.ones(len(codes))
    companies = [None] * len(codes)
    faretypes = [None] * len(codes)
    rcodes = np.NaN * np.ones(len(codes))
    # this should work with other webdrivers like Firefox, but phantomJS means no windows
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    logfile = open(path.join(outputpath, '{0}.log'.format(destination)), 'w')
    for count, code in enumerate(codes):
        if code in terminals:
            changes[count] = -1
        else:
            # query_url = baseurl.format(code, destination, time, date)
            query_url = baseurl.format(code, destination, date, time, arrdep)
            changes[count], jtime[count], driver = send_queryNRE(
                query_url, driver, dcap=dcap, debug=debug)
            if changes[count] > 1:
                nca = changes[count]
                jtimea = jtime[count]
                # minpricea = minprice[count]
                # maxpricea = maxprice[count]
                # meanpricea = meanprice[count]
                # query_url_dep = baseurl.format(code, destination, '0000d',
                #                                date)
                query_url_dep = baseurl.format(code, destination, date, '0000',
                                               'dep')
                ncd, jtimed, driver = send_queryNRE(
                    query_url_dep, driver, dcap=dcap, debug=debug)
                changes[count] = np.nanmin([nca, ncd])
                try:
                    jtime[count] = [jtimea, jtimed][np.nanargmin([nca, ncd])]
                    # minprice[count] = [minpricea,
                    #                    minpriced][np.nanargmin([nca, ncd])]
                    # maxprice[count] = [maxpricea,
                    #                    maxpriced][np.nanargmin([nca, ncd])]
                    # meanprice[count] = [meanpricea,
                    #                     meanpriced][np.nanargmin([nca, ncd])]

                except ValueError:
                    jtime[count] = np.NaN
                    # minprice[count] = np.NaN
                    # maxprice[count] = np.NaN
                    # meanprice[count] = np.NaN

        if np.isnan(changes[count]):
            if repeat_on_error is not None:
                ind = 0
                # datequery = '{0}-{1}-{2}'.format(year, month, day)
                datequery = '{0:02d}{1:02d}{2}'.format(day, month, year)
                while np.isnan(changes[count]) and ind < repeat_on_error:
                    # query_url_arr = baseurl.format(code, destination, time,
                    #                                datequery)
                    query_url_arr = baseurl.format(code, destination,
                                                   datequery, time, arrdep)
                    nca, jtimea, driver = send_queryNRE(
                        query_url_arr, driver, debug=debug, dcap=dcap)
                    # query_url_dep = baseurl.format(code, destination, '0000d',
                    #                                datequery)
                    query_url_dep = baseurl.format(code, destination,
                                                   datequery, '0000', 'dep')
                    ncd, jtimed, driver = send_queryNRE(
                        query_url_dep, driver, debug=debug, dcap=dcap)
                    changes[count] = np.nanmin([nca, ncd])
                    try:
                        jtime[count] = [jtimea,
                                        jtimed][np.nanargmin([nca, ncd])]
                        # minprice[count] = [minpricea,
                        #                    minpriced][np.nanargmin([nca, ncd])]
                        # maxprice[count] = [maxpricea,
                        #                    maxpriced][np.nanargmin([nca, ncd])]
                        # meanprice[count] = [meanpricea,
                        #                     meanpriced][np.nanargmin(
                        #                         [nca, ncd])]

                    except ValueError:
                        jtime[count] = np.NaN
                        # minprice[count] = np.NaN
                        # maxprice[count] = np.NaN
                        # meanprice[count] = np.NaN

                    ind += 1
                    # datequery = '{0}-{1}-{2}'.format(year, month, day + ind)
                    datequery = '{0:02d}{1:02d}{2}'.format(
                        day + ind, month, year)
                    print(
                        'repeating {1} for the {0} time.'.format(ind, code),
                        end='\r')
                    print('', end='\r')
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
        print(
            'station {0}/{1} complete'.format(count + 1, len(changes)),
            end='\r')
        print('', end='\r')
        fares[count], companies[count], faretypes[count], rcodes[
            count] = farequery(code, terminals[0])
    # remember to quit the webdriver and close logfile!
    driver.quit()
    logfile.close()
    # save as pickle
    pdict = {}
    pdict['names'] = names
    pdict['codes'] = codes
    pdict['changes'] = changes
    pdict['jtime'] = jtime
    # pdict['minprice'] = minprice
    # pdict['maxprice'] = maxprice
    # pdict['meanprice'] = meanprice
    pdict['fares'] = fares
    pdict['companies'] = companies
    pdict['faretypes'] = faretypes
    pdict['rcodes'] = rcodes
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
        # station_writer.writerow([
        #     'Name', 'Code',
        #     'Changes (-1 means terminus, 2 means 2+ changes, NaN means error or no connections possible)'
        # ])
        station_writer.writerow([
            'Name', 'Code', 'Changes', 'Time', 'Fare', 'Company', 'Fare Type',
            'Route Code'
        ])
        for name, code, change, jt, f, c, ft, rc in zip(
                names, codes, changes, jtime, fares, companies, faretypes,
                rcodes):
            station_writer.writerow([name, code, change, jt, f, c, ft, rc])
