import connection_count

year=2019
month=2
day=12
hhmm=2359
arrdep='a'
inputpath='/home/kinew/stations/'
outputpath='/home/kinew/stations/results/'
repeat_on_error=10


destination_list = ['london', 'birmingham', 'manchester', 'liverpool', 'sheffield', 'edinburgh', 'glasgow', 'southampton', 'leeds']
terminals_list=[[
    'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG',
    'MYB', 'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT',
    'WAE'
],
                ['BHM', 'BMO', 'BSW'],
                ['MAN', 'MCO', 'MCV', 'DGT'],
                ['LIV', 'LVC', 'LVJ', 'MRF'],
                ['SHF'],
                ['EDB', 'HYM'],
                ['GLC', 'GLQ'],
                ['SOU'],
                ['LDS']]

for destination, terminals in zip(destination_list, terminals_list):
    print('running for station {0}'.format(destination))
    connection_count.count(destination=destination,
                           terminals=terminals,
                           year=year,
                           month=month,
                           day=day,
                           hhmm=hhmm,
                           arrdep=arrdep,
                           inputpath=inputpath,
                           outputpath=outputpath,
                           repeat_on_error=repeat_on_error)
