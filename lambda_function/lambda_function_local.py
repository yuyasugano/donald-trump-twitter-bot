import os
import sys
import json
import boto3
import pickle
import tweepy

# Data Preprocessing and Feature Engineering
import re
import nltk
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# read envronment variables
consumer_key = os.environ['TW_CONSUMER_KEY']
consumer_secret = os.environ['TW_CONSUMER_SECRET']
access_token = os.environ['TW_ACCESS_TOKEN']
access_token_secret = os.environ['TW_ACCESS_TOKEN_SECRET']

def preprocessing(tweet):
        
    # Generating the list of words in the tweet (hastags and other punctuations removed)
    def form_sentence(tweet):
        tweet_blob = TextBlob(tweet)
        return ' '.join(tweet_blob.words)
    new_tweet = form_sentence(tweet)

    # Removing stopwords and words with unusual symbols
    def no_user_alpha(tweet):
        tweet_list = [ele for ele in tweet.split() if ele != 'user']
        clean_tokens = [t for t in tweet_list if re.match(r'[^\W\d]*$', t)]
        clean_s = ' '.join(clean_tokens)
        clean_mess = [word for word in clean_s.split() if word.lower() not in stopwords.words('english')]
        return clean_mess
    no_punc_tweet = no_user_alpha(new_tweet)
       
    # Normalizing the words in tweets 
    def normalization(tweet_list):
        lem = WordNetLemmatizer()
        normalized_tweet = []
        for word in tweet_list:
            normalized_text = lem.lemmatize(word,'v')
            normalized_tweet.append(normalized_text)
        return normalized_tweet

    return normalization(no_punc_tweet)

def tfidfvectorizer(local_file_path):

    # load TfidfVectorizer model
    with open(os.path.join(local_file_path, 'tfidf.pkl'), 'rb') as f:
        vec = pickle.load(f)
    print('TfidfVectorizer loaded successfully')
    return vec

def invokeandreturn(input_data, endpoint):

    client = boto3.client('sagemaker-runtime')
    response = client.invoke_endpoint(
        EndpointName = endpoint,
        Body = input_data.encode(),
        ContentType = 'text/csv',
        Accept = 'application/json'
    )
    return response

def lambda_handler(event, context):

    # initialize tweepy instance
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # add nltk corpus path with current local path
    nltk.data.path.append('./')
    api = tweepy.API(auth)
    value = int(event['number']) # how many tweets this function will check, usually one
    tweets = [tweet for tweet in tweepy.Cursor(api.user_timeline, id='realDonaldTrump').items(value) if (list(tweet.text)[:2]!=['R', 'T']) & (list(tweet.text)[0]!='@')]

    for tweet in tweets:
        tweet_id = tweet.id
        if tweet.retweeted == True:
            print('Retweeted already the tweet id: {}'.format(tweet_id))
        else:
            print('Tweet has not been retweeted')
            try:
                # obtain tfidfvectorizer model
                local_file_path = '/tmp'
                vec = tfidfvectorizer(local_file_path)

                pretweet = preprocessing(tweet.text)
                print('Raw text: {}'.format(tweet.text))
                print('Preprocessing tweet: {}'.format(pretweet))
                transform = vec.transform([tweet.text])
                print('Transformed tweet: {}'.format(transform))
                csv_transform = str(",".join(map(str, transform.toarray()[0])))
                # print('Input data to the endpoint: {}'.format(csv_transform))

                res = invokeandreturn(csv_transform, '<your sagemaker endpoint name>')
                prediction = res['Body'].read().decode('utf-8')
                print('Precition is: {}'.format(prediction))
                api.retweet(tweet.id)
                tweet_url = "https://twitter.com/{}/status/{}".format('realDonaldTrump', tweet.id)
                if int(prediction) == 0:
                    api.update_status('This is a positive tweet\n' + tweet_url)
                elif int(prediction) == 1:
                    api.update_status('This is a negative tweet\n' + tweet_url)

            except Exception as e:
                print(e)

# call lambda_hander
if __name__ == "__main__":
    print('Iteration of tweets: {}'.format(int(json.loads(sys.argv[1])['number'])))
    lambda_handler(json.loads(sys.argv[1]), {})

