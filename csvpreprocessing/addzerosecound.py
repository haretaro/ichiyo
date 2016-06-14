#coding: utf-8
import csv
with open('Y2013-all.csv','r') as f:
    data = csv.reader(f, delimiter=',')
    data = [[row[0], row[1]+':00'] + row[2:] for row in data]
    writer = csv.writer(open('output.csv','w'),delimiter=',')
    for row in data:
        writer.writerow(row)
        print(row)
