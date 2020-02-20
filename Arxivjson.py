import sqlite3
import operator
import io

##add function to produce JSON files for connected components##
def connectedComps(nodes,coauthors,names,ranks):
    x=-3
    fhand = io.open(names[nodes[x][0]]+'.js','w', encoding='utf-8')
    tempMap = dict()
    fhand.write('arXivJson = {"nodes":[\n')
    weight = str(len(set(coauthors[nodes[-1][0]])))
    fhand.write('{'+'"weight":'+weight+',"rank":'+str(ranks[nodes[x][0]])+',')
    fhand.write(' "id":'+str(nodes[x][0])+', "url":"'+names[nodes[x][0]]+'"}')
    tempMap[nodes[x][0]]=0
    count = 1
    for contributor in set(coauthors[nodes[x][0]]):
        if contributor in names:  ##if the coauthor is one of the top authors
            fhand.write(',\n')
            weight = str(len(set(coauthors[contributor])))
            fhand.write('{'+'"weight":'+weight+',"rank":'+str(ranks[contributor])+',')
            fhand.write(' "id":'+str(contributor)+', "url":"'+names[contributor]+'"}')
            tempMap[contributor]=count
            count+=1
    fhand.write('],\n')
    fhand.write('"links":[')
    for contributor in set(coauthors[nodes[x][0]]):
        if contributor in names:
            fhand.write('\n')
            projects=coauthors[nodes[x][0]].count(contributor)
            fhand.write('{"source":'+str(map[nodes[-1][0]])+',"target":'+str(tempMap[contributor])+',"value":'+str(projects)+'},')
    fhand.write(']};')
    fhand.close()
    return tempMap
            

conn = sqlite3.connect('arXiv.sqlite')
cur = conn.cursor()

print("Creating JSON output on arXiv.js...")
howmany = int(input("How many nodes? "))

cur.execute('''SELECT author_id, article_id
    FROM AuthorLinks''')# ON Pages.id = Links.to_id
    #WHERE html IS NOT NULL AND ERROR IS NULL
    #GROUP BY id ORDER BY id,inbound''')
    
count=dict()
for author in cur.fetchall():
    if not author[0] in count:
        count[author[0]] = 1
    else:
        count[author[0]] +=1
sorted_count = sorted(count.items(), key=lambda kv: kv[1])
#print(sorted_count[len(sorted_count)-howmany:)
final=len(sorted_count)
if howmany>final:
    print('Error, cannot use that many nodes')
    quit()
nodes = sorted_count[final-howmany:]
coauthors=dict()
names=dict()
#print(nodes)
for node in nodes[::-1]:
    coauthors[node[0]] = list()
    cur.execute("SELECT name FROM Author WHERE id=?", (node[0],))
    names[node[0]]=cur.fetchone()[0]
    cur.execute("SELECT article_id FROM AuthorLinks WHERE author_id=?", (node[0],))
    for paper in cur.fetchall():
        cur.execute("SELECT author_id FROM AuthorLinks WHERE article_id=?", (paper[0],))
        for contributor in cur.fetchall():
            if contributor[0]==node[0]: continue
            coauthors[node[0]].append(contributor[0])
    #print(coauthors[node[0]])
    

#print(names)
#cur.execute('''SELECT Author.name, AuthorLinks.author_id, AuthorLinks.article_id 
    #FROM Author JOIN AuthorLinks WHERE Author.id=AuthorLinks.author_id 
    #AND AuthorLinks.article_id=10198 AND EXISTS (SELECT article_id FROM 
    #AuthorLinks t2 WHERE AuthorLinks.article_id = t2.article_id GROUP BY 
    #t2.article_id HAVING count(t2.article_id)>1)''')

fhand = io.open('arXiv.js','w', encoding='utf-8')
maxrank = count[nodes[len(nodes)-1][0]]
minrank = count[nodes[0][0]]
#
#if maxrank == minrank or maxrank is None or minrank is None:
#    print("Error - please run sprank.py to compute page rank")
#    quit()

fhand.write('arXivJson = {"nodes":[\n')
count = 0
map = dict()
ranks = dict()
for row in nodes[::-1] :
    #if len(set(coauthors[row[0]]))<1: continue
    if count > 0 : fhand.write(',\n')
    print(row)
    rank = row[1]
    rank = 40 * ( (rank+1 - minrank) / (maxrank - minrank) )
    weight = str(len(set(coauthors[row[0]])))
    fhand.write('{'+'"weight":'+weight+',"rank":'+str(rank)+',')
    fhand.write(' "id":'+str(row[0])+', "url":"'+names[row[0]]+'"}')
    map[row[0]] = count
    ranks[row[0]] = rank
    count = count + 1
fhand.write('],\n')

#cur.execute('''SELECT DISTINCT from_id, to_id FROM Links''')
fhand.write('"links":[\n')

count = 0
#for x,y in itertools.combinations(range(0,len(nodes)-1),2):
for row in nodes:
    # print row
    if len(coauthors[row[0]])<1 : continue
    for contributor in set(coauthors[row[0]]):
        projects=coauthors[row[0]].count(contributor)
    #rank = ranks[row[0]]
    #srank = 19 * ( (rank - minrank) / (maxrank - minrank) ) 
        if contributor not in map: continue
        if count > 0 : fhand.write(',\n')
        fhand.write('{"source":'+str(map[row[0]])+',"target":'+str(map[contributor])+',"value":'+str(projects)+'}')
        count = count + 1
fhand.write(']};')
fhand.close()
#cur.close()
#
print("Open force2.html in a browser to view the visualization")
