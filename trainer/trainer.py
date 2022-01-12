import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score





def generate_Xy(mac, rawdf):

    df = rawdf[rawdf["MAC"] == mac]
    
    
    n = 20

    X = []
    y = []
    
    df.reset_index(inplace = True)
    gateways = df["gateway"].unique()
    gateways.sort()

    for i in range(len(df["rssi"][:-n])):
        entry = []
        for gw in gateways:
            k = 0
            points  = []
            while k< n:
                if df["gateway"][i+k] == gw:
                    points.append(df["rssi"][i+k])
                k = k+1
            if len(points)>0:
                entry.append(np.mean(points))
            else:
                entry.append(np.nan)
                
        X.append(entry)
    
    X = np.array(X)
    X = np.nan_to_num(X, nan = -100)

    for i in range(len(df["rssi"][:-n])):
    
        window = df[i:i+n].groupby("label").max()
        y.append(window.index[0])

    return X, y

def train_model(X, y):
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size= 0.7, test_size=0.3, random_state=1)
    knn = KNeighborsClassifier(n_neighbors= 10)
    knn.fit(X_train, y_train)

    return knn, accuracy_score(y_true= y_test, y_pred = knn.predict(X_test))




def train(file):

    rawdf = pd.read_csv(file, index_col=0)

    models = {}

    for mac in rawdf["MAC"].unique():

        X, y = generate_Xy(mac, rawdf)

        model, acc = train_model(X, y)

        print(f"{mac} Acc = {acc}")
    
        models[mac] = [model, acc]

    return models




#trainer("oficina6class.csv")