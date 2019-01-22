import numpy as np
import csv
import pickle
import os
from geopy import distance
from itertools import count


def grcsv(destination='london',
          destpath='/home/kinew/stations/results/NRE',
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
                for rcount, column in enumerate(row):
                    csvdict[headers[rcount]].append(column)

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
    jt = pdict['jtime']
    fares = pdict['fares']
    costpermin = fares / jt
    if terminal_llcol:
        conlat = np.array(pdict['lat'])
        termlat = conlat[ch < 0]
        conlon = np.array(pdict['lon'])
        termlon = conlon[ch < 0]
        mtlat = np.nanmean(termlat)
        mtlon = np.nanmean(termlon)
        dist = np.NaN * np.ones_like(conlon)
        for ind, clat, clon in zip(count(), conlat, conlon):
            if ~np.isnan(clat) and ~np.isnan(clon):
                dist[ind] = distance.distance((clat, clon), (mtlat, mtlon)).km
        costperkm = fares / dist
        crowspeed = dist / jt
        timeperkm = jt / dist
    if nanvalue is not None:
        ch[np.isnan(ch)] = nanvalue
        costpermin[np.isnan(costpermin)] = nanvalue
        if terminal_llcol:
            crowspeed[np.isnan(crowspeed)] = nanvalue
            costperkm[np.isnan(costperkm)] = nanvalue
            timeperkm[np.isnan(timeperkm)] = nanvalue
            dist[np.isnan(dist)] = nanvalue
        jt[np.isnan(jt)] = nanvalue
        fares[np.isnan(fares)] = nanvalue


    with open(outfile, 'w', newline='') as f:
        station_writer = csv.writer(f, delimiter=',')
        if terminal_llcol:
            station_writer.writerow([
                'Name', 'Code', 'Changes', 'lat', 'lon', 'terminal lat',
                'terminal lon', 'linear distance', 'Journey time', 'fare',
                'company', 'fare type', 'route code', 'cost per km', 'cost per min', 'speed (linear)', 'minutes to travel 1km linear'
            ])
        else:
            station_writer.writerow([
                'Name', 'Code', 'Changes', 'lat', 'lon', 'Journey time',
                'fare', 'company', 'fare type', 'route code'
            ])
        if terminal_llcol:
            for name, code, change, lat, lon, d, jti, f, c, ft, rc, cpkm, cpm, spd, tpkm in zip(
                    pdict['names'], pdict['codes'], ch, pdict['lat'],
                    pdict['lon'], dist, jt, fares, pdict['companies'],
                    pdict['faretypes'], pdict['rcodes'], costperkm, costpermin, crowspeed, timeperkm):

                station_writer.writerow([
                    name, code, change, lat, lon, mtlat, mtlon, d, jti, f, c,
                    ft, rc, cpkm, cpm, spd, tpkm
                ])

        else:
            for name, code, change, lat, lon, jti, f, c, ft, rc in zip(
                    pdict['names'], pdict['codes'], ch, pdict['lat'],
                    pdict['lon'], jt, fares, pdict['companies'],
                    pdict['faretypes'], pdict['rcodes']):

                station_writer.writerow(
                    [name, code, change, lat, lon, jti, f, c, ft, rc])

    print('ALL DONE :)')
