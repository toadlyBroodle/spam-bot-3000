# twatBot
A python command-line bot for automating promotion on social media. Scrape social media with custom queries and promote your product to all relevant results with a single command. <b>Use at your own risk:</b> depending on how specific your custom queries are, you could find yourself banned from associated social media sites very quickly ;)

## features
- Twitter
 - update user status
 - scan twitter for list of custom queries, dump results in local file (scrapeDump.txt)
  - favorite relevant tweets
  - follow original posters
  - reply to relevant tweets with random promotional tweet from file (promoTweets.txt)
  - write all activity to log (log.txt)

## quick setup
credentials.py
```
consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"
access_token = "your_access_token"
access_token_secret = "your_access_token_secret"
```

- create new 'credentials.py' file in main directory with your twitter credentials
 - <a href="https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library">a good guide for how to get credentials</a>
- replace promotional tweets (promoTweets.txt) with your own
 - individual tweets on seperate lines
 - each line must by <= 140 characters long
- replace search queries (queries.txt) with your own
 - individual queries on seperate lines
 - <a href="https://dev.twitter.com/rest/public/search">guide to constructing twitter queries</a>

## usage
twatBot.py [-s,--scrape-twitter \<n\> [-a,--favorite] [-o,--follow] [-p,--promote]] [-u,--update-status] [-h,--help]
: where \<n\> is number of tweets to scrape (n\<=200)
