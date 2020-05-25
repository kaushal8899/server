import pandas as pd
import numpy as np

def traindetails():
    pass

def getFlight(source,dest,date):
    flights = pd.read_csv('data/flights.csv')
    fl = []
    for i in range(len(flights)):
        f = flights.iloc[i]
        if(f['dst code']==dest):
            fl.append(dict(f))
    return fl

def getTrain(source,dest,date):
    trains = pd.read_csv('data/train.csv',na_values=['Nan','nan'])
    classes = trains.iloc[:,8:15]
    trains = trains.iloc[:,0:8]
    tr = []
    for i in range(len(trains)):
        t = trains.iloc[i]
        if(t['dest']==dest):
            dic = dict(t)
            cl = classes.iloc[i].fillna(0)
            print(cl)
            cl = pd.to_numeric(cl,downcast='integer')
            print(cl)
            dic['classes'] = list(cl)
            tr.append(dic)
    return tr

def getLocs():
    locs = pd.read_excel('data/locations.xlsx',na_values=['Not Specified','-'])
    locations = np.unique(locs['City/State'])
    return locations

def addloc(loc):
    locs = pd.read_excel('data/locations.xlsx',na_values=['Not Specified','-'],inplace=True)
    data = []
    data.append(loc)
    df = pd.DataFrame(data)
    locs.append(df,ignoe_index=True)

def updateloc(loc):
    pass

def getLocDetails(location):
    locs = pd.read_excel('data/locations.xlsx',na_values=['Not Specified','-'])
    details = locs[locs['City/State']==location]
    details = details.to_dict('list')
    details["count"] = len(details['Season'])
    return details

def getallLocations():
    locs = pd.read_excel('data/locations.xlsx',na_values=['Not Specified','-'])
    lo = []
    for i in range(len(locs)):
        lo.append(dict(locs.iloc[i]))
    return lo
