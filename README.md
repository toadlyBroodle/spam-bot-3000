# twatbot
Automated Promotion Bot - Twitter (query, favorite, follow, reply)

## quick setup
- replace twitter credentials (credentials.py) with your app's own
 - a good guide for how to get credentials: https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library
- replace promotional tweets (promoTweets.txt) with your own
 - individual tweets on seperate lines
 - each line must by <= 140 characters long
- replace search queries (queries.txt) with your own
 - individual queries on seperate lines
 - for list of twitter API operators see: https://dev.twitter.com/rest/public/search

## usage
twatBot.py [-s,--scrape-twitter \<n\> [-a,--favorite] [-o,--follow] [-p,--promote]] [-u,--update-status] [-h,--help]
: where \<n\> is number of tweets to scrape (n\<=200)
