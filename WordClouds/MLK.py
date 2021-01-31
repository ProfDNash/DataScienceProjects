# -*- coding: utf-8 -*-
"""
DR. MARTIN LUTHER KING JR. WORD CLOUD
Created on Mon Jan 18 13:19:53 2021

@author: David A. Nash
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

##read in data
with open('MLK.txt', 'r') as file:
    data = file.read().replace('\n', ' ')
Portrait = np.array(Image.open('MLKart.jpg'))


##define a function to preprocess the text
##Here, this includes removing parenthetical and bracket parts, as these are
##audience reactions

skipwords = ['negro','must','white','hate']

def preprocess(text):
    ##remove paretheticals and bracketed content
    no_paren = text.lower().replace('[','(')
    no_paren = no_paren.replace(']',')')
    no_paren = re.sub('\([^)]*\)',' ', no_paren)
    ##remove punctuation and stop words
    result = []
    stops = set(stopwords.words('english'))
    tokens = word_tokenize(no_paren)
    for t in tokens:
        if t not in stops and t not in skipwords and t.isalpha():
            result.append(t.lower())
    return result

filtered_words = preprocess(data)
##rejoin all filtered words into a single string
filtered_text = ' '.join(filtered_words)

##create Word Cloud object
wc = WordCloud(background_color='white', mask=Portrait, 
               stopwords=STOPWORDS,max_words=1000, width=1000, height = 1000)
wc.generate(filtered_text)

##create color_imprint
color_imprint = ImageColorGenerator(Portrait)
##Recolor the word cloud using the colors in the imprint
wc.recolor(color_func=color_imprint)
##export the wordcloud to a file
#wc.to_file('MLKcloud.png')

##Visualize the wordcloud
plt.figure(figsize=[8,11])
plt.imshow(wc,interpolation='bilinear')
plt.axis('off')
plt.show()