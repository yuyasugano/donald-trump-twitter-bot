## Twitter BOT with AWS Lambda and SageMaker

Sentiment analysis Twitter BOT with AWS Lambda and SageMaker.

## Overview

This is my simple experiment to create a twitter BOT reacting to our controversial president Donald Trump's great tweets and generate retweets with sentiment analysis by AWS Lambda and SageMaker. I used scikit-learn to train twitter corpus and deployed an inference endpoint on AWS SageMaker. Twitter bot part is coded in Lambda and it retweets his tweets with positive or negative label. We call this lambda function periodically by CloudWatch Event and this goes to check his recent tweets.

## Files

1. `Twitter Sentiment Analysis using NLTK, Python for Donald Trump.ipynb` is local test on Jupyter Notebook to train a model before implementing on SageMaker.
2. TBD

## License

This library is licensed under the Apache 2.0 License.
