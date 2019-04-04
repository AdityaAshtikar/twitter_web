from django.shortcuts import render, redirect
from django.http import HttpResponse

from mysite.settings import STATIC_URL as STATIC
import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

def index2(request):
    return render(request, 'twitter/index2.html')

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
        '''
        if analysis.sentiment.polarity >= 0.5:
            if analysis.sentiment.polarity > 0:
                pos_correct += 1
        '''
        threshold = 0.001
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity >= threshold:
            if analysis.sentiment.polarity > 0:
                return 'positive'
        elif analysis.sentiment.polarity <= -threshold: 
            if analysis.sentiment.polarity <= 0:
                return 'negative'
        else: 
            return 'neutral'
  
    def get_tweets(self, query, count = 10, typeOfTweets = 'mixed'): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = []
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = query + "-filter:retweets", count = count, result_type = typeOfTweets)
  
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
                # parsed_tweet['likes'] = tweet._json['favorite_count']
                # parsed_tweet['likes'] = tweet.user['entities']['favourites_count']
                parsed_tweet['likes'] = tweet.favorite_count

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
    typeOfTweets = request.GET['typeOfTweets']
    response.write("<html><head><title>Search Results: {}</title><link rel=stylesheet href=https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'></head><body><div class=container>" . format(query))
    response.write("<h3>Search results for: <em>{}</em></h3><hr>" . format(query))
    # calling function to get tweets 
    tweets = api.get_tweets(query, count, typeOfTweets)
    # HttpResponse(tweets)
    tcount = 1
    response.write("<h3><a class='btn btn-info' href=/twitter/>Search Again..</a></h3>")
    if len(tweets) <= 0 and int(count) > int(100):
        return redirect(index)
    else:
        response.write("<h2 style='color: purple;'>Number of clean tweets rendered: <b>{}</b></h2><p>" . format(len(tweets)))
    response.write("<hr>") 
    positiveLikes = 0
    negativeLikes = 0
    positiveLikesPercent = 0
    negativeLikesPercent = 0
    for tweet in tweets:
        # average of positive and negative tweets for predictability and giving colors
        if tweet['sentiment'] == 'positive':
            sentimentColor = 'green'
            positiveLikes = positiveLikes + tweet['likes']
        elif tweet['sentiment'] == 'negative':
            sentimentColor = 'red'
            negativeLikes = negativeLikes + tweet['likes']
        else:
            sentimentColor = 'yellow'
        totalLikes = positiveLikes + negativeLikes
        if not positiveLikes == 0:
            positiveLikesPercent = (positiveLikes/totalLikes) * 100
        if not negativeLikes == 0:
            negativeLikesPercent = (negativeLikes/totalLikes) * 100
        response.write("<div class='card'>")
        response.write("<p class='card-header'>{}.) </p>" .format(tcount))
        response.write("<div class='card-header'><span style='color: grey'>Text: </span><b style='color: blue'>{}</b></div>". format(tweet['text']))
        tcount += 1
        response.write("<div class='card-body'>")
        response.write("<div class='card-text'><span style='color: grey'>Sentiment: </span><b style='color: " + sentimentColor + "'><u>{}</u></b></div>". format(tweet['sentiment']))
        # calculating polarity of text
        '''
        analysis = TextBlob(self.clean_tweet(tweet)) 
        # set sentiment 
        if analysis.sentiment.polarity >= threshold:
            if analysis.sentiment.polarity > 0:
                return 'positive'
        '''
        analysis = TextBlob(tweet['text'])
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        '''
        if polarity in +ve, +ve tweet, else -ve tweet
        '''
        response.write("<br><div style='width: 80%; margin-left: 15px;'>")
        response.write("<img style='max-width: 80%; position: absolute;' src='" + STATIC + "grey.jpg' height=5px width=100%>")
        if tweet['sentiment'] != 'neutral':
            if analysis.sentiment.polarity > 0.0:
                response.write("<img style='max-width: 100%; position: relative;' src='" + STATIC + "green.png' height=5px width={}%>" . format(polarity * 100))
                response.write("<br>Polarity: +{}%".format(polarity * 100))
            elif analysis.sentiment.polarity < 0.0:
                response.write("<img style='max-width: 100%; position: relative;' src='" + STATIC + "red.jpg' height=5px width={}%>" . format(abs(polarity) * 100))
                response.write("<br>Polarity: {}%".format(polarity * 100))
        else:
            response.write("<br>Polarity: 0")
        response.write("</div><br>")
        if analysis.detect_language() != "en":
            response.write("<div class='card-text'><span style='color: grey'>Language: </span><b style='color: black'>{}</b></div>". format(analysis.detect_language()))
        response.write("<div class='card-text'><span style='color: grey'>Subjectivity (0 - objective | 1 - subjective): </span><b style='color: black'>{}</b></div>". format(subjectivity))
        # plotting subjectivity graph
        response.write("<div style='width: 80%; margin-left: 15px;'>")
        response.write("<img style='max-width: 80%; position: absolute;' src='" + STATIC + "grey.jpg' height=5px width=100%>")
        response.write("<img style='max-width: 100%; position: relative;' src='" + STATIC + "blue.png' height=5px width={}%>" . format(subjectivity * 100))
        response.write("<br>Subjectivity: {}%".format(subjectivity * 100))
        response.write("</div><br>")
        response.write("<div class='card-text'><span style='color: grey'>Username: </span><b style='color: black'>{}</b></div>". format(tweet['username']))
        response.write("<div class='card-text'><span style='color: grey'>Created At: </span><b style='color: black'>{}</b></div>". format(tweet['created_at']))
        response.write("</div>") # card-body
        response.write("<div class='card-footer'>")
        response.write("<h5><span style='color: grey'>Location: </span><b style='color: black'><u>{}</u></b></h5>". format(tweet['location']))
        response.write("<h5 style='float: right;'><span style='color: grey'>Likes: </span><b style='color: black'><u>{}</u></b></h5>". format(tweet['likes']))
        response.write("</div>")
        response.write("</div>")
        # response.write("<hr>")
    response.write("<h4>Predictability: </h4><br>")
    if positiveLikesPercent == 0 and negativeLikesPercent == 0:
        response.write("<b>Not predictable!</b><br><br>")
    else:
        response.write("<img src='" + STATIC + "green.png' height=35 width={}%>" . format(positiveLikesPercent))
        response.write("<img src='" + STATIC + "red.jpg' height=35 width={}%><br><br>" . format(negativeLikesPercent))
    response.write("<span style='color: green;'>Likes for positive tweets: {} ( {}% )</span><br>" . format(positiveLikes, positiveLikesPercent))
    response.write("<span style='color: red;'>Likes for negative tweets: {} ( {}% )</span>" . format(negativeLikes, negativeLikesPercent))
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # p=(100*len(ptweets)/len(tweets))
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # n=(100*len(ntweets)/len(tweets))
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
    response.write("<hr><h3><a class='btn btn-info' href=/twitter/>Search Again..</a></h3></body>")
    return response

# if __name__ == "__main__": 
   
#     main()