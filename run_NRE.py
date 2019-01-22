import connection_count
import make_georef_csv

year = 19
month = 2
day = 12
hhmm = 2359
arrdep = 'arr'
inputpath = '/home/kinew/stations/'
outputpath = '/home/kinew/stations/results/NRE/'
repeat_on_error = 10

# destination_list = [
#     'london', 'birmingham', 'manchester', 'liverpool', 'sheffield',
#     'edinburgh', 'glasgow', 'southampton', 'leeds', 'bradford', 'leicester', 'nottingham',
#     'chelmsford', 'reading', 'newcastle', 'cambridge', 'crewe', 'bradford',
#     'preston', 'exeter', 'norwich', 'warrington', 'watford', 'shrewsbury'
# ]
# terminals_list = [[
#     'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG', 'MYB',
#     'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT', 'WAE'
# ], ['BHM', 'BMO', 'BSW'], ['MAN', 'MCO', 'MCV', 'DGT'],
#                   ['LIV', 'LVC', 'LVJ', 'MRF'], ['SHF'], ['EDB', 'HYM'],
#                   ['GLC', 'GLQ'], ['SOU'], ['LDS'], ['BDI', 'BDQ'], ['LEI'], ['NOT'], ['CHM'],
#                   ['RDG', 'RDW'], ['NCL'], ['CBG'], ['CRE'], ['BDQ', 'BDI'],
#                   ['PRE'], ['EXD', 'EXT', 'EXC'], ['NRW'], ['WBQ', 'WAC'],
#                   ['WFH', 'WFJ', 'WFN', 'WFS', 'WFW'], ['SHR']]

destination_list = [
    'birmingham', 'manchester', 'liverpool', 'sheffield', 'edinburgh',
    'glasgow', 'southampton', 'leeds', 'bradford', 'leicester', 'nottingham',
    'chelmsford', 'reading', 'newcastle', 'cambridge', 'crewe', 'bradford',
    'preston', 'exeter', 'norwich', 'warrington', 'watford', 'shrewsbury'
]

terminals_list = [['BHM', 'BMO', 'BSW'], ['MAN', 'MCO', 'MCV', 'DGT'],
                  ['LIV', 'LVC', 'LVJ', 'MRF'], ['SHF'], ['EDB', 'HYM'],
                  ['GLC', 'GLQ'], ['SOU'], ['LDS'], ['BDI', 'BDQ'], ['LEI'],
                  ['NOT'], ['CHM'], ['RDG', 'RDW'], ['NCL'], ['CBG'], ['CRE'],
                  ['BDQ', 'BDI'], ['PRE'], ['EXD', 'EXT', 'EXC'], ['NRW'],
                  ['WBQ', 'WAC'], ['WFH', 'WFJ', 'WFN', 'WFS', 'WFW'], ['SHR']]

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
        outfile='{1}{0}_geo.csv'.format(destination, outputpath),
        nanvalue=-999,
        terminal_llcol=True)
