import connection_count
import make_georef_csv

year = 2019
month = 2
day = 12
hhmm = 2359
arrdep = 'a'
inputpath = '/home/kinew/stations/'
outputpath = '/home/kinew/stations/results/'
repeat_on_error = 10

destination_list = [
    'leicester', 'nottingham', 'chelmsford', 'reading', 'newcastle',
    'cambridge', 'crewe', 'bradford', 'preston', 'exeter', 'norwich',
    'warrington', 'watford', 'shrewsbury'
]
terminals_list = [['LEI'], ['NOT'], ['CHM'], ['RDG', 'RDW'], ['NCL'], ['CBG'],
                  ['CRE'], ['BDQ', 'BDI'], ['PRE'], ['EXD', 'EXT', 'EXC'],
                  ['NRW'], ['WBQ', 'WAC'], ['WFH', 'WFJ', 'WFN', 'WFS', 'WFW'],
                  ['SHR']]
for destination, terminals in zip(destination_list, terminals_list):
    print('running for station {0}'.format(destination))
    connection_count.count(
        destination=destination,
        terminals=terminals,
        year=year,
        month=month,
        day=day,
        hhmm=hhmm,
        arrdep=arrdep,
        inputpath=inputpath,
        outputpath=outputpath,
        repeat_on_error=repeat_on_error)

    make_georef_csv.grcsv(
        destination=destination,
        outfile='/home/kinew/stations/results/{0}_geo.csv'.format(destination),
        nanvalue=-999,
        terminal_llcol=True)
