Bus Price setter and follower detection


Idea                                                                                                                              The main idea behind our approach was to find the buses with the least price and recorded time difference for a given date of travel, then the bus which preceded the other bus in the recorded time is taken to be followed by the other. Thus we ended up taking 2 variables as our dimensions for clustering: the price and the time dimension.


Execution

Preprocessing                                                                                                                                                   The data had two columns for the price, for different kinds of seats. For each row, at least one of these was empty. We removed the rows which had 0 or NaN for both of these. Some of the data points had more than one value for the price, so we separated these into different rows, taking these as different data points. The ‘RecordedAt’ column was converted into an integer and then scaled such that the values lie between 0 to 500 as this gave optimal clustering. The ‘Bus’ field contained strings and thus a mapping was required for easy manipulation. Hence we assigned each bus a numerical value from 0 to 116.

Clustering                                                                                                                                                      We divided the dataset into 16 parts with respect to the travel (service) date. In each of these, we clustered the buses with respect to two dimensions - the price and the time of the purchase(recorded time). This was done using K Means clustering. We used the elbow method to find the number of clusters, which was 3-4 in every case. So we chose to have 4 clusters for each date. 

Confidence Scores                                                                                                                                              In these clusters, we calculated the confidence scores such that the minimum price difference would fetch the highest value of confidence. We achieved this by taking the difference of the price of the ticket and then scaled this value with respect to the price of those two tickets. We even assigned positive or negative values for a given pair of buses in a cluster based on whether their ‘RecordedAt’ field was less or more in magnitude. Then we took the average of all the confidence scores obtained between any two buses from all the clusters of all the dates. Finally we also made sure that our final results are not misaligned due to lack of data and therefore we scaled our final output score accordingly if the number of results between any two particular buses , i.e. frequency of having them in the same cluster over the dataset is less than 5, which we kept as the threshold.

Output                                                                                                                                                         After calculating the confidence scores, we found out the highest positive and negative confidence score for each bus, which gave us the best possible buses which follow and are followed by that bus respectively. 


Conclusion
The final output we obtained is the .csv file. All the buses with negative confidence scores were the ones that followed some other bus, meanwhile a positive score meant that the bus is followed by some other bus. Finally we converted the obtained .csv file into the required format and decided followers and followed by using the sign and mentioned the respective modulus of the confidence score.

