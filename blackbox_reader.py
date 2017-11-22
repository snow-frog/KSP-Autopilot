import csv
import matplotlib.pyplot as plt
data = []

def plotsingle(datatype,data):
    plt.plot(range(len(data)),data)
    plt.xlabel('Time')
    plt.ylabel(legend[choice])
    plt.show()

def plottriple(datatype,data):
    d1 = []
    d2 = []
    d3 = []
    plt.title(datatype)
    for i in data:
        x = i.replace(')','').replace('(','').replace(' ','').split(',')
        d1.append(x[0])
        d2.append(x[1])
        d3.append(x[2])
    plt.plot(range(len(data)),d1, color="red",label="Pitch")
    plt.plot(range(len(data)),d2, color="blue",label="Yaw")
    plt.plot(range(len(data)),d3, color="green",label="Roll")
    plt.legend(loc='upper left', frameon=True)
    plt.show()

filename = '2017-11-22_023205.csv'
with open(filename, 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        data.append(row)
legend = data.pop(0)

while 1:
    print 'Select data to view'
    for i in range(len(legend)):
        print i,legend[i]
    print''
    choice = int(raw_input("> "))
    
    plotdata = []
    for i in data:
        plotdata.append(i[choice])
    if choice>21:
        plottriple(legend[choice],plotdata)
    else:
        plotsingle(legend[choice],plotdata)
    
    print''
