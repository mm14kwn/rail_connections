import numpy as np
import csv
import pickle

# load in connection data
with open('station_connections.pickle', 'rb') as f:
    pdict = pickle.load(f)

with open('station_latlon.csv') as f:
    read_csv = csv.reader(f, delimiter=',')
    hcount = 0
    headers=[]
    csvdict = {}
    for row in read_csv:
        if hcount==0:
            for column in row:
                headers.append(column)
                csvdict[column] = []
            hcount = 1
        else:
            for count,column in enumerate(row):
                csvdict[headers[count]].append(column)
                
