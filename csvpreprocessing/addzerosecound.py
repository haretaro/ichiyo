#coding: utf-8
#日付の秒をゼロで埋める
import csv
with open('result_nikkei30min.csv','r') as f:
    data = csv.reader(f, delimiter=',')
    data = [[row[0], row[1]+':00'] + row[2:] for row in data]
    writer = csv.writer(open('output.csv','w'),delimiter=',')
    for row in data:
        writer.writerow(row)
        print(row)
