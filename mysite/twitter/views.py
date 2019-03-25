from django.shortcuts import render, redirect
from django.http import HttpResponse

from clint.textui import colored
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

def index(request):
    return render(request, 'twitter/index.html')

class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        response = HttpResponse()
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = 'KurKqm7zDgQAOGe20d6C477Vn'
        consumer_secret = 'eaEmpDVncnoMWkjQDVu3fUsD9VRyf3UqRZTx7eMko70ZEndXG7'
        access_token = '1067804649938272256-0TWU4H5UBetjinQpWDrOxE8bQXMYmn'
        access_token_secret = 'PxRrqHe8ugkwZKV9r4xN8JjsCu9KWftM0sM2QGMafq17V'
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            response.write("Error: Authentication Failed") 
    def clean_tweet(self, tweet): 
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])  |(\w+:\/\/\S+)", " ", tweet).split()) 
    def get_tweet_sentiment(self, tweet): 
        ''' 
        Utility function to classify sentiment of passed tweet 
        using textblob's sentiment method 
        '''
        # create TextBlob object of passed tweet text 
        # HttpResponse(tweet)
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'
  
    def get_tweets(self, query, count = 10): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = []
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query, count = count) 
  
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

                parsed_tweet['created_at'] = tweet.created_at
                parsed_tweet['username'] = tweet.user.screen_name
                parsed_tweet['location'] = tweet.user.location

                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
            # return parsed tweets 
            return tweets 
        except tweepy.TweepError as e: 
            # HttpResponse error (if any) 
            HttpResponse("Error : " + str(e))

def main(request): 
    # creating object of TwitterClient Class 
    api = TwitterClient() 
    response = HttpResponse()
    query = request.GET['searchQuery']
    count = request.GET['count']
    response.write("<html><head><title>Search Results: {}</title><link rel=stylesheet href=https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'></head><body><div class=container>" . format(query))
    response.write("<h3>Search results for: <em>{}</em></h3><hr>" . format(query))
    # calling function to get tweets 
    tweets = api.get_tweets(query, count)
    # HttpResponse(tweets)
    tcount = 1
    response.write("<h3><a class='btn btn-info' href=/twitter/>Search Again..</a></h3>")
    if len(tweets) <= 0:
        return redirect(index)
    else:
        response.write("<h2 style='color: purple;'>Number of clean tweets rendered: <b>{}</b></h2><p>" . format(len(tweets)))
    response.write("<hr>")
    for tweet in tweets:
        response.write("<p>{}.) " .format(tcount))
        response.write("<h3><span style='color: grey'>Text: </span><b style='color: blue'>{}</b></h3><p>". format(tweet['text']))
        tcount += 1
        response.write("<h4><span style='color: grey'>Sentiment: </span><b style='color: black'><u>{}</u></b></h4><p>". format(tweet['sentiment']))
        response.write("<h4><span style='color: grey'>Username: </span><b style='color: black'><u>{}</u></b></h4><p>". format(tweet['username']))
        response.write("<h4><span style='color: grey'>Created At: </span><b style='color: black'><u>{}</u></b></h4><p>". format(tweet['created_at']))
        response.write("<h4><span style='color: grey'>Location: </span><b style='color: black'><u>{}</u></b></h4><p>". format(tweet['location']))
        response.write("<hr>")
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    p=(100*len(ptweets)/len(tweets))
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    n=(100*len(ntweets)/len(tweets))
    nu_tweets = (len(tweets) - len(ntweets) - len(ptweets))
    # percentage of positive tweets 
    response.write("<hr>")
    if (len(ptweets) > len(ntweets) and len(ptweets) > nu_tweets):
        response.write("<h1 style='color: green;'>Positive tweets percentage: {} % </h1>".format(100*len(ptweets)/len(tweets)))
    else:  
        response.write("<h1>Positive tweets percentage: {} %</h1>".format(100*len(ptweets)/len(tweets)))
    response.write("<hr>")
    # percentage of negative tweets 
    if(len(ntweets) > len(ptweets) and len(ntweets) > nu_tweets):
        response.write("<h1 style='color: red'>Negative tweets percentage: {} %</h1>".format(100*len(ntweets)/len(tweets)))
    else:
        response.write("<h1>Negative tweets percentage: {} %</h1>".format(100*len(ntweets)/len(tweets)))
    response.write("<hr>")
    # percentage of neutral tweets
    if(nu_tweets > len(ptweets) and nu_tweets > len(ntweets)):
        response.write("<h1 style='color: yellow;'>Neutral tweets percentage: {} %</h1>".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))
    else:
        response.write("<h1>Neutral tweets percentage: {} %</h1>".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))
    # response.write(ing first 5 positive tweets 
    response.write("<hr>")
    response.write("<p>Top 5 Positive tweets:")
    for tweet in ptweets[:5]: 
        response.write("<p style='color: green'> {}</p>".format(tweet['text']))
    # response.write(ing first 5 negative tweets 
    response.write("<hr><p>Top 5 Negative tweets:") 
    for tweet in ntweets[:5]: 
        response.write("<p style='color: red'> {}</p>".format(tweet['text']))
    response.write("<br><hr><h3><a class='btn btn-info' href=/twitter/>Search Again..</a></h3></body>")
    return response

# if __name__ == "__main__": 
   
#     main()