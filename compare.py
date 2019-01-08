import numpy as np
import csv
from itertools import compress

with open('results.csv') as f:
    read_csv = csv.reader(f, delimiter=',')
    hcount = 0
    headers=[]
    fitnrdict = {}
    for row in read_csv:
        if hcount==0:
            for column in row:
                headers.append(column)
                fitnrdict[column] = []
            hcount = 1
        else:
            for count,column in enumerate(row):
                fitnrdict[headers[count]].append(column)
                

with open('london_connections.csv') as f:
    read_csv = csv.reader(f, delimiter=',')
    hcount = 0
    headers=[]
    kinewdict = {}
    for row in read_csv:
        if hcount==0:

            headers=['Name', 'Code', 'Changes']
            for key in headers:
                kinewdict[key] = []
            hcount = 1
        else:
            for count,column in enumerate(row):
                kinewdict[headers[count]].append(column)
                

kinewdirectcode = []
for count, x in enumerate(kinewdict['Changes']):
    if float(x)==0:
        kinewdirectcode.append(kinewdict['Code'][count])

knotf = np.setdiff1d(kinewdirectcode,fitnrdict['stop_id'])
fnotk = np.setdiff1d(fitnrdict['stop_id'],kinewdirectcode)


with open('differences.txt','w') as f:
    f.write('stops found as direct by KW_Newman and not fitnr:\n')
    for stop in knotf:
        f.write('{0}\n'.format(stop))
    f.write('stops found as direct by fitnr and not KW_Newman:\n')
    for stop in fnotk:
        f.write('{0}\n'.format(stop))
