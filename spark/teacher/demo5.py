import sys
from pyspark import SparkContext
from __future__ import print_function
#given the list of neighbors for a page and that page's rank, calculate
#what that page contributes to the rank of its neighbors

def computeContribs(neighbors, rank):
    for neighbor in neighbors:
        yield(neighbor, rank/len(neighbors))

#read in a file of page links (format: url1 url2)
linkfile = "pagelinks.txt"
sc = SparkContext(appName="pagerank")
links = sc.textFile(linkfile).map(lambda line : line.split())\
        .map(lambda pages: (pages[0], pages[1])).distinct().groupByKey().persist() #filter out duplicates

# set initial page ranks to 1.0
ranks = links.map(lambda (page, neighbors): (page, 1.0))

#number of iterations
n = 10

# for n iterations, calculate new page ranks based on neighbor contributions
for x in xrange(n):
    contribs=links\
        .join(ranks)\
        .flatMap(lambda (page, (neighbors, rank)):computeContribs(neighbors, rank))
        #(page1, ([page2, page3], 1.0))

    ranks=contribs\
        .reduceByKey(lambda v1,v2: v1+v2)\
        .map(lambda (page,contrib): \
            (page, contrib * 0.85 + 0.15))
    print "Iteration ",x
    for pair in ranks.take(10): print pair

sc.stop()



