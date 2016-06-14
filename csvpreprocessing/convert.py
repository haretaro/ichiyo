#coding: utf-8
#5分足のcsvファイルから時間足を作る
import csv
from datetime import datetime, timedelta
START = 1#始値の列番号(0が日付, 1 2 3 4のどれか)
END = 2
MAX = 3
MIN = 4

#時間足データの作成
def makecsv(delta, hourly=True):
    f = open('nikkei5min.csv','r')
    data = csv.reader(f, delimiter=',')
    data = [[row[0] + ' ' + row[1]] + row[2:] for row in data]#一列目と２列目の連結
    data = [[datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S')] + row[1:] for row in data]#一列目をdatetime型に変換

    output = []
    start = data[0]
    rowtemp = start
    for row in data:
        if(row[0] - start[0] < delta):
            rowtemp[END] = row[END]
            rowtemp[MIN] = min(row[MIN], rowtemp[MIN])
            rowtemp[MAX] = max(row[MAX], rowtemp[MAX])
        else:
            output.append(rowtemp)
            start = row
            #お昼が12:30から始まるが12:00から計算する
            if hourly and start[0].minute == 30:
                start[0] = start[0].replace(minute = 0)
            rowtemp = start
    output.append(rowtemp)
    
    for row in output:
        row[0] = datetime.strftime(row[0],'%Y/%m/%d %H:%M:%S')
    return output

    f.close()

data = makecsv(timedelta(hours=1))
writer = csv.writer(open('hourly.csv','w'), delimiter=',')
for row in data:
    writer.writerow(row)
    print(row)


data = makecsv(timedelta(minutes=30), hourly=False)
writer = csv.writer(open('30minutes.csv','w'), delimiter=',')
for row in data:
    writer.writerow(row)
    print(row)
