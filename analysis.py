from __future__ import division  # Python 2 users only
import nltk, re, pprint, datetime, os
from nltk import word_tokenize
from nltk.book import *
from nltk.corpus import stopwords
from collections import Counter

'''
To analyze data, there are two possible configurations:
1) argument for FreqDist (set to 25, but you can change this)
2) teamswcolors (can include all 30 teams or pick and choose)

http://danielsussman.com/prawbot/about.html
'''

today = datetime.date.today()
excluded = []
stopwords = stopwords.words('english')
other = ['\'S','N\'T', '\'M', '\'RE', '\'VE', '\'LL']
for i in stopwords:
	excluded.append(str(i).upper())
for j in other:
	excluded.append(j)

def freq(team, color):
	raw = open(team, 'r').read()
	tokens = word_tokenize(raw)
	text = nltk.Text(tokens)
	global excluded
	clean = [w for w in text if w not in excluded]
	results = FreqDist(clean).most_common(25) #list of tuples, so re-arrange below
	out = []
	for i in results:
		x = i[0].title() #keyword
		y = i[1] #number of occurences
		out.append([x, float("{0:.2f}".format(100*(y/len(text)))), color]) #[keyword, occurences per 100 words, team color]
	return str(out)[1:] #TODO: find ideal storage method for retrieval rather than manual upload

#files for coding tokens as positive or negative
pos = open('pos_neg/williamgunn_positive.txt').read() #see Hu and Liu (http://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html)
neg = open('pos_neg/williamgunn_negative.txt').read() #or https://github.com/williamgunn/SciSentiment

def posemo(team):
    text = open(team).read()
    p=0
    n=0
    for word in word_tokenize(text):    
        if word.lower() in word_tokenize(pos):
            p=p+1
        if word.lower() in word_tokenize(neg):
            n=n+1
    pp = 100*(p/len(word_tokenize(text)))
    pn = 100*(n/len(word_tokenize(text)))
    return [pn, pp, ((pp-pn)/pp), len(word_tokenize(text))] 

teamswcolors = [['ATL', '#e74c3c'], ['BKN', '#34495e'], ['BOS', '#2ecc71'], ['CHA', '#3498db'], ['CHI', '#e74c3c'], 
	['CLE', '#c0392b'], ['DAL', '#2980b9'], ['DEN', '#f39c12'], ['DET', '#e74c3c'], ['GSW', '#3498db'], ['HOU', '#c0392b'],
	['IND', '#f39c12'], ['LAC', '#e74c3c'], ['LAL', '#9b59b6'], ['MEM', '#2980b9'], ['MIA', '#c0392b'], ['MIL', '#2ecc71'],
	['MIN', '#2980b9'], ['NOP', '#e74c3c'], ['NYK', '#d35400'], ['OKC', '#2980b9'], ['ORL', '#2980b9'], ['PHI', '#e74c3c'],
	['PHX', '#d35400'], ['POR', '#e74c3c'], ['SAC', '#9b59b6'], ['SAS', '#7f8c8d'], ['TOR', '#9b59b6'], ['UTA', '#f1c40f'],
	['WAS', '#e74c3c']]

''' Perform sentiment and frequency analysis '''
pos_neg_data = []
ratio_data = []
file = open(os.path.join("data", "freq", "2014-12-04.txt"), "w")
for i in teamswcolors:
	filename = 'data/corpora/'+i[0]+'_'+str(today.isoformat())+'.txt'
	j = posemo(filename)
	pos_neg_data.append([j[0], j[1], i[0]]) #[neg, pos, team name]... TO-DO: optimize for automation
	ratio_data.append([i[0], j[2]]) #[team name, (pos-neg)/pos]... TO-DO: optimize for automation
	file.write(i[0]+":"+"\n")
	file.write(freq(filename, i[1])) #performs the frequency analysis
	file.write("\n")
	file.write("\n")
file.close()

file = open(os.path.join("data", "posemo", str(today.isoformat())+"_pos_neg.txt"), "w")
file.write(str(pos_neg_data))
file.close()

file = open(os.path.join("data", "posemo", str(today.isoformat())+"_ratio.txt"), "w")
file.write(str(ratio_data))
file.close()

''' TODO: Find application for search, most likely a two-series line chart '''
'''
def search(term, team1, team2):
	x = term.upper()
	corpus1 = open('data/corpora/'+team1+'_'+str(today.isoformat())+'.txt').read()
	corpus2 = open('data/corpora/'+team2+'_'+str(today.isoformat())+'.txt').read()
	count1 = corpus1.count(x)
	count2 = corpus2.count(x)
	percent1 = 100*corpus1.count(x)/len(word_tokenize(corpus1))
	percent2 = 100*corpus2.count(x)/len(word_tokenize(corpus2))
	return team1+": "+str(count1)+" occurences, "+str(percent1)+" percent"+"\n"+team2+": "+str(count2)+" occurences, "+str(percent2)+" percent"
'''
