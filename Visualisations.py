#############################################################################################
# Author: Matthew Borowski                                                                 #
# Date Created: Monday 27/04/2023 12:47                                                     #
# Project Name: Detecting non-compliance therapeutic goods selling on e-commerce websites.  #
# Project Group ID: 9785-23-06                                                              #
#############################################################################################

#%% import packages
import pandas as pd
import numpy as np

#%% import csv file
df = pd.read_csv('complete-results_2023-04-26.csv')
# dropping useless unnamed/old index column
df = df.drop(df.columns[0], axis = 1)

#%% using a temp dataframe to maintain the integrity fo the original dataset
dfTemp = df

#%% finds the unique observations based on the name of the product
dfTemp = dfTemp.drop_duplicates(subset = ['Name'], keep='first')


# %%

#print(dfTemp.groupby(['CompFinal']).count())

import matplotlib.pyplot as plt

#shows the number of non-compliant products we detected
FinalComplianceDf = dfTemp['CompFinal'].value_counts()

plotCompliance = FinalComplianceDf.plot.bar(x = 'index', y = 'CompFinal', rot=0)
plotCompliance.bar_label(plotCompliance.containers[0])
plt.title('Vitamins & Supplements Compliancy')
plt.xlabel('Compliancy Status')
plt.ylabel('Number of Occurrences')
print(plotCompliance)

#%%
#Shows number of correct guesses vs incorrect
SystemCorrectGuesses = dfTemp['GuessOutcome'].value_counts()
#plotGuesses = dfTemp['GuessOutcome'].value_counts().plot(kind='bar')
plotGuesses = SystemCorrectGuesses.plot.bar(x='index', y='', rot=0)
plotGuesses.bar_label(plotGuesses.containers[0])
plt.title('System Guesses (Vitamins & Supplements)')
plt.xlabel('Guess Status')
plt.ylabel('Number of Occurrences')
print(plotGuesses)






# %%
