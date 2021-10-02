
# R-Tree Implementation and Search Query 

This project was another university assignment for the subject 
'COMP3210 Big Data'. It involved tinkering with an R-tree 
implementation we studied and created in lectures. For those
who are unaware, an R-tree is a B-tree (Tree with more than 
two child nodes per parent node) where the data of each node 
has two or more dimensions. 

In this project we worked on many relevant methods and 
functions for our R-tree implementation such as: creation 
of nodes and trees, deletion of nodes and trees, addition 
of nodes, overload handling and many more. 

One important function that we then created and investigated
was a range search query, where we used the R-tree to search
a region for any data points. We then compared its time taken
to that of a simple 'sequential-scan' search, which simply
involves a linear search of the region in question. 
Unsurprisingly, the search taking advantage of the R-tree 
structure was much faster than its linear alternative.  






