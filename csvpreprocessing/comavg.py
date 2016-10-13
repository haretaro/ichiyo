# IPython log file


import csv
data = []

with open("companyAverage.csv","r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)
        
f = open("nikkei5min_2.txt","r")
nreader = csv.reader(f)

ndata = []
for e in nreader:
    ndata.append(e)
    
for e in ndata:
    if e[0] == "end":
        break
    e.append(data[0][e[0]])
    
rf = open("result_nikkei5min.csv","w")
for e in ndata:
        for ec in e:
                rf.write(ec + ",")
        rf.write("\n")
        
rf.close()

