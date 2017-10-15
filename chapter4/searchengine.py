from collections import defaultdict
import sqlite3

class searcher:
    def __init__(self,dbname):
        self.con=sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self,q):
        # Strings to build the query
        fieldlist='w0.urlid'
        tablelist=''
        clauselist=''
        wordids=[]

        # Split the words by spaces
        words=q.split(' ')
        tablenumber=0

        for word in words:
            # Get the word ID
            wordrow=self.con.execute("select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1

        # Create the query from the separate parts
        fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
        print(fullquery)
        cur=self.con.execute(fullquery)
        rows=[row for row in cur]

        return rows,wordids

    def getscoredlist(self, rows, wordids):
        totalscores = dict([(row[0], 0) for row in rows])

        # This is where we'll put our scoring functions
        weights = [(1.0, self.locationscore(rows)),
                   (1.0, self.frequencyscore(rows)),
                   (1.0, self.distancescore(rows)),
                   #(1.0, self.pagerankscore(rows)),
                   #(1.0, self.linktextscore(rows, wordids)),
                   #(5.0, self.nnscore(rows, wordids))
                   ]
        for (weight, scores) in weights:
            for url in totalscores:
                totalscores[url] += weight * scores[url]

        return totalscores

    def geturlname(self,id):
        return self.con.execute(
        "select url from urllist where rowid=%d" % id).fetchone()[0]

    def query(self,q):
        rows,wordids=self.getmatchrows(q)
        if len(rows) == 0:
            print("None found")
            return
        scores=self.getscoredlist(rows,wordids)
        rankedscores=[(score,url) for (url,score) in scores.items()]
        rankedscores.sort()
        rankedscores.reverse()
        for (score,urlid) in rankedscores[0:10]:
            print ('%f\t%s' % (score,self.geturlname(urlid)))
        return wordids,[r[1] for r in rankedscores[0:10]]

    def normalizescores(self,scores,smallIsBetter=0):
        if len(scores) == 0:
            return defaultdict()
        vsmall=0.00001 # Avoid division by zero errors
        if smallIsBetter:
            minscore=min(scores.values())
            return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
        else:
            maxscore=max(scores.values())
            if maxscore==0: maxscore=vsmall
            return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])

    def frequencyscore(self,rows):
        counts=dict([(row[0],0) for row in rows])
        for row in rows: counts[row[0]]+=1
        return self.normalizescores(counts)

    def locationscore(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]: locations[row[0]] = loc
        return self.normalizescores(locations, smallIsBetter=1)

    def distancescore(self, rows):
        # If there's only one word, everyone wins!
        if len(rows[0]) <= 2: return dict([(row[0], 1.0) for row in rows])

        # Initialize the dictionary with large values
        mindistance = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < mindistance[row[0]]: mindistance[row[0]] = dist
        return self.normalizescores(mindistance, smallIsBetter=1)

s = searcher('craigslist.db')
s.query("honda panda fast car truck")
