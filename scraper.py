import praw, datetime, os, operator
from operator import itemgetter

'''
For scraping data, there are two possible configurations: 
1) num_submissions and num_user_comments
2) teams (can include all 30 teams or pick and choose)

http://danielsussman.com/prawbot/about.html
'''

today = datetime.date.today()
num_submissions = 100 #how many threads to look at (for getting usernames)
num_user_comments = 2 #how many comments to take from users, at most
'''
TO-DO: CREATE A UNIQUE USER AGENT:
r=praw.Reddit(user_agent="    ")
'''
submissions = r.get_subreddit('nba').get_top(limit=num_submissions)

total_users = {} #all users who have commented in the threads viewed
flair_recognized = 0 #users with a flair that can be assigned to a team
total_comments = 0 #all comments in the threads viewed
user_comments = 0 #comments used in forming all corpora

class Fanbase(object):

	def __init__(self, name, flairs):
		self.name = name
		self.flairs = flairs
		flairs.append(name)
		self.users = {}

	def __str__(self):
		return self.name+": "+str(self.users)

ATL = Fanbase('ATL', ['Hawks'])
BKN = Fanbase('BKN', ['Nets', 'New Jersey Nets', 'Brooklyn Nets', 'Joe Johnson'])
BOS = Fanbase('BOS', ['Celtics', 'Avery Bradley'])
CHA = Fanbase('CHA', ['Hornets', 'Bobcats'])
CHI = Fanbase('CHI', ['Bulls', 'Derrick Rose', 'Pau Gasol'])
CLE = Fanbase('CLE', ['Cavaliers', 'Anderson Varejao', '[Brazil] Anderson Varejao', '[NBA] LeBron James'])
DAL = Fanbase('DAL', ['Mavericks', 'Mavs', 'Dirk Nowitzki'])
DEN = Fanbase('DEN', ['Nuggets', 'Ty Lawson'])
DET = Fanbase('DET', ['Pistons'])
GSW = Fanbase('GSW', ['Warriors'])
HOU = Fanbase('HOU', ['Rockets'])
IND = Fanbase('IND', ['Pacers'])
LAC = Fanbase('LAC', ['Clippers', 'Braves', 'San Diego Clippers'])
LAL = Fanbase('LAL', ['Lakers', 'Kobe Bryant', 'Kobe', 'Minneapolis Lakers'])
MEM = Fanbase('MEM', ['Grizzlies', 'Vancouver Grizzlies'])
MIA = Fanbase('MIA', ['Heat'])
MIL = Fanbase('MIL', ['Bucks', '[NBA] Jabari Parker'])
MIN = Fanbase('MIN', ['Timberwolves', 'Wolves'])
NOP = Fanbase('NOP', ['Pelicans', 'Jrue Holiday'])
NYK = Fanbase('NYK', ['Knicks', 'KnickerBockers'])
OKC = Fanbase('OKC', ['Thunder', '[SEA]', 'Supersonics', 'Kevin Durant'])
ORL = Fanbase('ORL', ['Magic'])
PHI = Fanbase('PHI', ['76ers', 'Sixers'])
PHX = Fanbase('PHX', ['Suns', '[PHO] Gerald Green'])
POR = Fanbase('POR', ['Trail Blazers'])
SAC = Fanbase('SAC', ['Kings'])
SAS = Fanbase('SAS', ['Spurs', 'Kawhi Leonard'])
TOR = Fanbase('TOR', ['Raptors'])
UTA = Fanbase('UTA', ['Jazz'])
WAS = Fanbase('WAS', ['Wizards', 'Bullets'])

teams = [ATL, BKN, BOS, CHA, CHI, CLE, DAL, DEN, DET, GSW, HOU, IND, LAC, LAL, MEM, MIA,
            MIL, MIN, NOP, NYK, OKC, ORL, PHI, PHX, POR, SAC, SAS, TOR, UTA, WAS]

for submission in submissions:
    submission.replace_more_comments(limit=5, threshold=10) # looks at the MoreComments object
    flat_comments = praw.helpers.flatten_tree(submission.comments)
    total_comments = total_comments+submission.num_comments
    for comment in flat_comments:
        if comment.author is None:
            pass # happens when a comment has been deleted, so skip
        else:
            u = str(unicode(comment.author).encode('ascii', 'replace'))
            f = str(unicode(comment.author_flair_text).encode('ascii', 'replace'))
            total_users.update({u: f})
            for team in teams:
                if (f in team.flairs) or ("["+team.name+"]" in f): #will match: [ATL] Jeff Teague
                    team.users.update({u: f})

def build(input):
    output = ''
    for u, f in input.users.iteritems():
        for comment in r.get_redditor(u).get_comments(limit=num_user_comments):
            global user_comments
            user_comments+=1
            raw = ' '.join(str(unicode(comment.body).encode('ascii', 'replace')).split())
            clean = ''.join(c for c in raw if c not in ('!','.',':','?','*','%','\'','"','\'s','-','(',')',',','=','/',';','&','[',']','^'))
            output+=clean.upper()+' '
    return output

''' Build a corpus for each team and create a file for it '''
for team in teams:
    file = open(os.path.join("data", "corpora", team.name+"_"+str(today.isoformat())+".txt"), "w")
    file.write(build(team))
    file.close()

''' Print some info about the build '''
flair_recognized = 0
for team in teams:
    flair_recognized+=len(team.users) #count the users associated with a specific team
build_info = str(num_submissions)+" threads ("+str(total_comments)+" total comments viewed),"+"\n"+str(len(total_users))+" users ("+str((len(total_users)-flair_recognized))+" with unrecognized flair),"+"\n"+str(user_comments)+" comments stored"+"\n"+"\n"
print build_info

''' Create a file about the users '''
file = open(os.path.join("data", "users", str(today.isoformat())+".txt"), "w")
file.write(build_info)
sorted_users = sorted(total_users.items(), key=operator.itemgetter(1)) #sort alphabetically by flair
for u, f in sorted_users:
    line = str(u)+": "+str(f)+"," + '\n' #username, flair
    file.write(line)
file.close()
