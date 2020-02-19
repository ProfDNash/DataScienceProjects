# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 05:53:41 2020

@author: Nash
"""

##GATHER DATA FROM arXiv.sqlite DATABASE FOR VISUALIZATION##
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect('arxiv.sqlite')#(r'C:\Users\Nash\Desktop\arXiv.sqlite')
cur = conn.cursor()

TrueNames = {
        "math.AG": "Algebraic Geometry",
        "math.AT": "Algebraic Topology",
        "math.AP": "Analysis of PDEs",
        "math.CT": "Category Theory",
        "math.CA": "Classical Analysis and ODEs",
        "math.CO": "Combinatorics",
        "math.AC": "Commutative Algebra",
        "math.CV": "Complex Variables",
        "math.DG": "Differential Geometry",
        "math.DS": "Dynamical Systems",
        "math.FA": "Functional Analysis",
        "math.GM": "General Mathematics",
        "math.GN": "General Topology",
        "math.GT": "Geometric Topology",
        "math.GR": "Group Theory",
        "math.HO": "History and Overview",
        "math.IT": "Information Theory",
        "math.KT": "K-Theory and Homology",
        "math.LO": "Logic",
        "math.MP": "Mathematical Physics",
        "math.MG": "Metric Geometry",
        "math.NT": "Number Theory",
        "math.NA": "Numerical Analysis",
        "math.OA": "Operator Algebras",
        "math.OC": "Optimization and Control",
        "math.PR": "Probability",
        "math.QA": "Quantum Algebra",
        "math.RT": "Representation Theory",
        "math.RA": "Rings and Algebras",
        "math.SP": "Spectral Theory",
        "math.ST": "Statistics Theory",
        "math.SG": "Symplectic Geometry",
        "math-ph": "Physics, Mathematical"
        }


##First, gather data about the number of articles in each category##
yearList = ['92','93','94','95','96','97','98','99','00','01','02','03','04','05',
            '06','07','08','09','10','11','12','13','14','15','16','17','18','19']
yearCounts = pd.DataFrame(columns=['Year', 'Category', 'Count'])
names = list()
counts = list()
pal = sns.color_palette('bright',10)+sns.color_palette('dark',10)+sns.color_palette('pastel',10)+sns.color_palette('Set1',10)

def gatherData():
    global yearList
    global yearCounts
    global names
    global counts
    cur.execute("SELECT subject, id FROM Classification")
    LST = cur.fetchall()
    row = 0
    for cat in LST:
        if "math" not in cat[0]: continue  ##skip non-math classifications
        names.append(TrueNames[cat[0]])
        annualCounts = list()
        for year in yearList: 
            st = '5'+ year + '%'
            cur.execute("SELECT COUNT(article_id) FROM ClassLinks WHERE subject_id =? AND article_id LIKE ?", (cat[1],st,))
            annualCounts.append(cur.fetchone()[0])
            if 90<int(year)<100: 
                yearLabel='19'+year
            else:
                yearLabel='20'+year
            yearCounts.loc[row] = [yearLabel,TrueNames[cat[0]],annualCounts[-1]]
            row+=1
        counts.append(sum(annualCounts))
  
    

##Plot Total Counts##
def plotTotals(names, counts):
    data = {"Category":names, "Number of Articles":counts}
    df = pd.DataFrame(data)
    df = df.sort_values(by=["Number of Articles"])
    plt.figure(figsize=(10,5))
    chart = sns.barplot(x=df["Category"], y=df["Number of Articles"], palette='Set1')
    chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
    #df.plot.bar(x='Category', y='Number of Articles', legend=None)
    #sns.barplot(x=df["Category"], y=df["Number of Articles"])
    #sns.set_palette(sns.color_palette('Set1',len(df)))
    #sns.set_palette(pal,len(df))
    #ax1.set_prop_cycle('color', colors)
    plt.title('Total Number of Articles by Category', color='black')
    plt.savefig('Totals.png', bbox_inches='tight')
    plt.show()

##Plot Counts by Year##
def plotLines():
    #yC = yearCounts.pivot(index='Year', columns='Category', values = 'Count')
    yearCounts.Year = yearCounts.Year.astype(int)
    yearCounts.Count = yearCounts.Count.astype(int)
    plt.figure(figsize=(10,9))
    sns.set_palette(pal, len(yC))
    LP = sns.lineplot(x='Year', y='Count', hue='Category', data=yearCounts, markers=range(len(yC)), palette=pal[:31])
    #ax2 = yC.plot(xticks=range(len(yC)))
    #sns.set_palette(sns.color_palette("Set1", len(yC)))
    LP.set_xticklabels(labels=yearCounts.Year,rotation=90)
    LP.set(xticks=yearCounts.Year)
    plt.ylabel("Number of Articles (per Year)")
    #ax2.set_prop_cycle('color', colors)
    plt.title('Contributions by Category', color='black')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.savefig('ByYear.png',bbox_inches='tight')
    plt.show()
    

##Plot Counts by Year##
def plotAreas(pal):
    yearCounts.Year = yearCounts.Year.astype(int)
    yearCounts.Count = yearCounts.Count.astype(int)
    yC = yearCounts.pivot(index='Year', columns='Category', values = 'Count')
    plt.figure(figsize=(10,9))
    sns.set_palette(pal, len(yC))
    plt.stackplot(yC.index.values, np.array(yC).transpose(), labels=yC.columns, colors=pal)
    plt.xticks(ticks=yC.index.values,rotation=90)
    plt.ylabel("Number of Articles (per Year)")
    plt.xlabel("Year")
    plt.title('Contributions by Category', color='black')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    #plt.legend(loc='upper left', bbox_to_anchor=(0.01, 1), ncol=3)
    plt.savefig('AreaByYear.png',bbox_inches='tight')
    plt.show()