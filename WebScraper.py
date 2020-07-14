"""
WEB SCRAPER (Gather Data on Sentence Commutations from Justice Department Website)
Create pandas dataframe that contains the data, and check for how many of the
sentences that were commuted by President Obama were for drug related offenses.

@author: David A. Nash
"""
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.justice.gov/pardon/obama-commutations'
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
p_tags = soup.findAll('p')
textList = []
for elm in p_tags:
        textList.append(elm.text)

##Now try to pull individual records
recordList = []
for i in range(len(textList)):
    if 'Offense' in textList[i]:
        ##find next appearance of "Offense"
        j = i+1
        while j<len(textList) and 'Offense' not in textList[j]:
            j+=1
        record=''
        if j==len(textList)-1: j+=2
        for k in range(i-1,j):
            record+=textList[k]
        ##adjust record for easy splitting
        record = record.replace('Offense:', '!')
        record = record.replace('District/Date:', '!')
        record = record.replace('Sentence:', '!')
        record = record.replace('Terms of grant:', '!')
        record = record.replace('Terms of Grant:', '!')  ##entries are not organized consistently
        record = record.replace('\xa0', '') ##delete strange code that appears occassionally
        record = record.split('!')
        ##further split District and Date
        record.insert(3,record[2].split(';')[1])
        record[2] = record[2].split(';')[0]
        recordList.append(record)

##setup DataFrame to hold the information
DF = pd.DataFrame(columns=['Name', 'Offense', 'District', 'Date', 'Sentence', 'Terms of Grant'], data=recordList)

Drug = 0
for off in DF.Offense:
    if 'cocaine' in off or 'marijuana in off' or 'drug' in off:
        Drug+=1
print('Number of sentences commuted which were due to a drug related offense:', Drug)

DF.to_csv('ObamaCommuteData.csv')


