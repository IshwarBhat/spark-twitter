import tweepy
import sys
import json
import urllib
import boto3

__author__ = 'anirban'

consumer_key = 'EGzM90F5SHXhZtE8jH1eutC17'
consumer_secret = 'gIgxq50KM3SpRbrIxaKa4ffaiowEo8aB4Lhm8POis3o2iO0jve'
access_token = '3259887824-HA2NR6WHBPggQLi8P98mpUWCbok27wGoS5yHG9H'
access_token_secret = '7kQZSdzC9VfHgmpgjoH7PJPu8WXkQdo0O04HCjLqZXiB4'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

searchQuery = 'Donald Trump'
fName = searchQuery+".json"
searchQuery = urllib.quote(searchQuery)
maxTweets = 100000
tweetsPerQry = 100

sinceId = None

max_id = -1L

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
with open(fName, 'w') as f:
    #f.write('TweetText|*|PossiblySensitive|*|RetweetCount|*|Language|*|CreationTime|*|Place|*|UserMentions|*|Hashtags|*|Urls')
    f.write('\n')
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                JsonString = json.dumps(tweet._json)
                Json = json.loads(JsonString)
                f.write(JsonString)
                '''TweetText = Json['text']
                TweetText = TweetText.replace('\n', ' ')
                RetweetCount = Json['retweet_count']
                PossiblySensitive=None
                if 'possibly_sensitive' in Json:
                    PossiblySensitive=Json['possibly_sensitive']
                Entities = Json['entities']
                UserMentions = Entities['user_mentions']
                Hashtags = Entities['hashtags']
                Urls = Entities['urls']
                Language = unicode(Json['lang'])
                CreationTime = unicode(Json['created_at'])
                Place = unicode(Json['place'])
                Text = str(TweetText.encode('utf-8'))+'|*|'+str(PossiblySensitive)+'|*|'+str(RetweetCount)+'|*|'+str(Language)+'|*|'+str(CreationTime)+'|*|'+str(Place.encode('utf-8'))+'|*|'
                f.write(Text)
                for i in range(0, len(UserMentions)):
                    f.write((UserMentions[i]['screen_name']).encode('utf-8'))
                    if i is not len(UserMentions)-1:
                        f.write(',')
                f.write('|*|')
                for i in range(0, len(Hashtags)):
                    f.write((Hashtags[i]['text']).encode('utf-8'))
                    if i is not len(Hashtags)-1:
                        f.write(',')
                f.write('|*|')
                for i in range(0, len(Urls)):
                    f.write((Urls[i]['url']).encode('utf-8'))
                    if i is not len(Urls)-1:
                        f.write(',')'''
                f.write('\n')
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            print("some error : " + str(e))
            break

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))
print ("Transferring file to S3 bucket...")
import boto3
s3 = boto3.resource('s3')
s3.meta.client.upload_file(fName, 'myasubucket', fName)
print ("Transfer complete!")
