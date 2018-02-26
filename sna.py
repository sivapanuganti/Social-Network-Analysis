print ()

import networkx
from operator import itemgetter
import matplotlib.pyplot

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])
    
# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past

#     Get the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.
purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph,purchasedAsin,radius=1)
print ('Purchased Asin Ego Graph:',
       'Number of Nodes= ', purchasedAsinEgoGraph.number_of_nodes(),
       'Number of Edges= ', purchasedAsinEgoGraph.number_of_edges())


# Next, recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
 
#     Use the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph
threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()

for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e ['weight'] > threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,e)

print('Purchased_Asin_Ego_Trim_Graph:',
         'threshold=', threshold,
         'Nodes=', purchasedAsinEgoTrimGraph.number_of_nodes(),
         'Edges=', purchasedAsinEgoTrimGraph.number_of_edges())

# Next, recall that given the purchasedAsinEgoTrimGraph you constructed above, 
# you can get at the list of nodes connected to the purchasedAsin by a single 
# hop (called the neighbors of the purchasedAsin) 

#     Find the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors
purchasedAsinNeighbors = []
purchasedAsinNeighbors = purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)
print("Neighbors of the purchasedAsin:", purchasedAsinNeighbors)
print("Number of trimmed neighbours of ",purchasedAsin,"=",len(purchasedAsinNeighbors))
print()
# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff

#     Note that, given an asin, you can get at the metadata associated with  
#     it using amazonBooks (similar to lines 49-56 above).
#     Now, come up with a composite measure to make Top Five book 
#     recommendations based on one or more of the following metrics associated 
#     with nodes in purchasedAsinNeighbors: SalesRank, AvgRating, 
#     TotalReviews, DegreeCentrality, and ClusteringCoeff 
N,NR=0,0
for i in purchasedAsinNeighbors:
    NR=NR+(amazonBooks[i]['TotalReviews']*amazonBooks[i]['AvgRating'])
    N=N+amazonBooks[i]['TotalReviews']

ranking=[]
for i in purchasedAsinNeighbors:
    temp=(NR+(amazonBooks[i]['TotalReviews']*amazonBooks[i]['AvgRating']))/(N+amazonBooks[i]['TotalReviews'])
    ranking.append([i,round(temp,4)])
recommendations=list(reversed(sorted(ranking,key=itemgetter(1))))[:4]

# Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff)
  
for i in range(len(recommendations)):
    print()
    print ("ASIN = ", recommendations[i][0]) 
    print ("Title = ", amazonBooks[recommendations[i][0]]['Title'])
    print ("SalesRank = ", amazonBooks[recommendations[i][0]]['SalesRank'])
    print ("TotalReviews = ", amazonBooks[recommendations[i][0]]['TotalReviews'])
    print ("AvgRating = ", amazonBooks[recommendations[i][0]]['AvgRating'])
    print ("DegreeCentrality = ", amazonBooks[recommendations[i][0]]['DegreeCentrality'])
    print ("ClusteringCoeff = ", amazonBooks[recommendations[i][0]]['ClusteringCoeff'])
