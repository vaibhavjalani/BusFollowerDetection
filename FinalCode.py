# -*- coding: utf-8 -*-
# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from statsmodels import api as sm
import numpy as np
import missingno as msno

#Loading data
path = input("Enter path to dataset")
df = pd.read_csv(path)
X = df

pd.set_option('display.max_rows', 80)
pd.set_option('display.max_columns', 10)
np.set_printoptions(threshold = np.inf)

bus = X['Bus'].unique()

mapping = {}
c = 0

for id in bus:
    mapping[id] = c
    c += 1

#drop rows having both Seat Fare Type 1 and 2 as NaN
X.dropna(subset=['Seat Fare Type 1', 'Seat Fare Type 2'], how='all', inplace=True)

#Splitting lists in Seat fare type 1 to separate rows (called 'exploding')
SFT1 = X['Seat Fare Type 1'].str.split(',')
X['Seat Fare Type 1'] = SFT1
X=X.explode('Seat Fare Type 1', ignore_index=True)

#Splitting lists in Seat fare type 2 to separate rows (called 'exploding')
SFT2 = X['Seat Fare Type 2'].str.split(',')
X['Seat Fare Type 2'] = SFT2
X=X.explode('Seat Fare Type 2', ignore_index=True)

#Convert object data to float data
X[['Seat Fare Type 1', 'Seat Fare Type 2']] = X[['Seat Fare Type 1', 'Seat Fare Type 2']].apply(pd.to_numeric, errors='coerce')

#Merging sft1 and sft2 and adding a new column which indicates the type of fare
X['Fare Type'] = np.where(np.isnan(X['Seat Fare Type 1'].values), 2, 1)
X['Seat Fare Type 1'] = X['Seat Fare Type 1'].fillna(X['Seat Fare Type 2'])
X.rename(columns={'Seat Fare Type 1':'Seat Fare'}, inplace = True)
X.drop('Seat Fare Type 2', axis=1, inplace=True)

#convert string to date time format
X['RecordedAt'] = pd.to_datetime(X['RecordedAt'], format='%d-%m-%Y %H:%M')
X['Service Date'] = pd.to_datetime(X['Service Date'], format='%d-%m-%Y %H:%M')

#Remove zero rows
X = X.loc[(X['Seat Fare']!=0)]

#Convert dates to integer taking 01-01-1970 00:00:00 as reference
X['RecordedAt'] = X['RecordedAt'].apply(lambda x: x.value)


#Mix Max scaling for RecordedAt column
from sklearn.preprocessing import MinMaxScaler
mm_X = MinMaxScaler()
X['RecordedAt'] = mm_X.fit_transform(X['RecordedAt'].to_numpy().reshape(-1,1))
X['RecordedAt'] *= 500


#Replace the strings in Bus by integers following the mapping dictionary
X.replace({'Bus': mapping}, inplace=True)

#group the dataframe by Service Date
gp = X.groupby('Service Date')

from sklearn.cluster import KMeans
wcss=[]

for i in range(1,21):
    kmeans=KMeans(n_clusters=i,init='k-means++',max_iter=300,n_init=10,random_state=0)
    kmeans.fit(gp.get_group('2020-07-15')[['Seat Fare', 'RecordedAt']])
    wcss.append(kmeans.inertia_)

plt.plot(range(1,21),wcss)
plt.show()

confidence_score = np.zeros((117,117))
frequency = np.zeros((117,117))

#group the dataframe by Service Date
gp = X.groupby('Service Date')

dates = {0 : '2020-07-15', 1 : '2020-07-16', 2 : '2020-07-17', 3: '2020-07-18', 4: '2020-07-19', 5: '2020-07-20', 6: '2020-07-21', 7: '2020-07-22', 8: '2020-07-23', 9: '2020-07-24', 10: '2020-07-25', 11: '2020-07-26', 12: '2020-07-27', 13: '2020-07-28', 14: '2020-07-29', 15: '2020-07-30'}

# when comparing <A,B> if A has lesser RecordedAt value, then give +ve sign to confidence_score[A][B]
# when comparing <A,B> if A has more RecordedAt value, then give -ve sign to confidence score for confidence_score[A][B]

for i in range(16):
    X_day = gp.get_group(dates[i])
    kmeans=KMeans(n_clusters=4,init='k-means++',max_iter=300,n_init=10,random_state=0)

    y_kmeans = kmeans.fit_predict(X_day[['Seat Fare', 'RecordedAt']])
    # centroids = kmeans.cluster_centers_

    X_day['clusters'] = kmeans.labels_
    gps = X_day.groupby('clusters')

    for i in range(4):
        X_day_cluster = gps.get_group(i)
        X_day_cluster.sort_values(['Bus', 'RecordedAt'], ascending = [True, True], inplace = True)

        X_day_cluster = X_day_cluster.drop_duplicates(subset=['Bus'], keep='first')

        for i, row_i in X_day_cluster.iterrows():
            A = row_i
            for j, row_j in X_day_cluster.iterrows():
                B = row_j

                if not(i == j):
                    A_code = int(A['Bus'])
                    B_code = int(B['Bus'])

                    if(A['RecordedAt'] > B['RecordedAt']):
                        confidence_score[A_code, B_code] += -1 + abs(A['Seat Fare'] - B['Seat Fare'])/(A['Seat Fare'] + B['Seat Fare'])
                        frequency[A_code, B_code] += 1
                    else:
                        confidence_score[A_code, B_code] += 1 - abs(A['Seat Fare'] - B['Seat Fare'])/(A['Seat Fare'] + B['Seat Fare'])
                        frequency[A_code, B_code] += 1

# print(pd.DataFrame(confidence_score))

for i in range(117):
    for j in range(117):
        if(frequency[i, j] > 5):
            confidence_score[i, j] = confidence_score[i, j] / frequency[i, j]
        else:
            confidence_score[i, j] = confidence_score[i, j] / 5

follows_cf = []
followedby_cf = []

follows = []
followedby = []

def get_key(val):
    for key, value in mapping.items():
         if val == value:
             return key

for i in range(117):
    maxInColumns = np.amax(confidence_score[i,:], axis=0)
    minInColumns = np.amin(confidence_score[i,:], axis=0)

    follows_cf.append(abs(minInColumns))
    followedby_cf.append(maxInColumns)

    max_index = confidence_score[i,:].argmax(axis=0)
    min_index = confidence_score[i,:].argmin(axis=0)

    if(minInColumns == 0):
        follows.append("")
    else:
        follows.append(get_key(min_index))
    
    if(maxInColumns == 0):
        followedby.append("")
    else:
        followedby.append(get_key(max_index))

submission = pd.DataFrame(
    {'Bus': bus,
     'Follows': follows,
     'Confidence Score (Follows)': follows_cf,
     'Is followed by': followedby,
     'Confidence Score (Is followed by)': followedby_cf}
)

submission.to_csv('PGI6512_Enigma_output.csv',index=False)