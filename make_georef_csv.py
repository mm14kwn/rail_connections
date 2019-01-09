import numpy as np
import csv
import pickle
import os


def grcsv(destination='london',
          destpath='/home/kinew/stations/results/',
          llpath='/home/kinew/stations/station_latlon.csv',
          outfile='/home/kinew/stations/results/london_geo.csv',
          nanvalue=None,
          terminal_llcol=False):
    # load in connection data
    with open(
            os.path.join(destpath,
                         '{0}_connections.pickle'.format(destination)),
            'rb') as f:
        pdict = pickle.load(f)

    with open(llpath) as f:
        read_csv = csv.reader(f, delimiter=',')
        hcount = 0
        headers = []
        csvdict = {}
        for row in read_csv:
            if hcount == 0:
                for column in row:
                    headers.append(column)
                    csvdict[column] = []
                hcount = 1
            else:
                for count, column in enumerate(row):
                    csvdict[headers[count]].append(column)

    stllcodes = csvdict['TLC']
    stlat = csvdict['Latitude']
    stlon = csvdict['Longitude']
    pdict['lat'] = []
    pdict['lon'] = []
    for code in pdict['codes']:
        if code in stllcodes:
            pdict['lat'].append(float(stlat[stllcodes.index(code)]))
            pdict['lon'].append(float(stlon[stllcodes.index(code)]))
        else:
            print('station {0} not in llfile'.format(code))
            pdict['lat'].append(np.NaN)
            pdict['lon'].append(np.NaN)

    ch = pdict['changes']
    if terminal_llcol:
        conlat = np.array(pdict['lat'])
        termlat = conlat[ch < 0]
        conlon = np.array(pdict['lon'])
        termlon = conlon[ch < 0]
        mtlat = np.nanmean(termlat)
        mtlon = np.nanmean(termlon)
        dist = np.sqrt((conlat - mtlat)**2 + (conlon - mtlon)**2)
    if nanvalue is not None:
        ch[np.isnan(ch)] = nanvalue

    with open(outfile, 'w', newline='') as f:
        station_writer = csv.writer(f, delimiter=',')
        if terminal_llcol:
            station_writer.writerow([
                'Name', 'Code', 'Changes', 'lat', 'lon', 'terminal lat',
                'terminal lon', 'linear distance'
            ])
        else:
            station_writer.writerow(['Name', 'Code', 'Changes', 'lat', 'lon'])
        if terminal_llcol:
            for name, code, change, lat, lon, d in zip(
                    pdict['names'], pdict['codes'], ch, pdict['lat'],
                    pdict['lon'], dist):

                station_writer.writerow(
                    [name, code, change, lat, lon, mtlat, mtlon, d])

        else:
            for name, code, change, lat, lon in zip(
                    pdict['names'], pdict['codes'], ch, pdict['lat'],
                    pdict['lon']):

                station_writer.writerow([name, code, change, lat, lon])

    print('ALL DONE :)')
