__author__ = 'Esther'

import sqlite3
import soundex

import soundex_config
import tweepy
import random

def login():
    # for info on the tweepy module, see http://tweepy.readthedocs.org/en/

    # Authentication is taken from soundex_config.py
    consumer_key = soundex_config.consumer_key
    consumer_secret = soundex_config.consumer_secret
    access_token = soundex_config.access_token
    access_token_secret = soundex_config.access_token_secret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

def stick_together_output(dbpath):
    connection = sqlite3.connect(dbpath)
    c = connection.cursor()

    while True:
        try:
            attempts = 0
            firstword = c.execute('select word from lemmas where rowid = ( abs(random() % (select count(*) from lemmas) - 1)) + 1 ;')
            firstword = firstword.fetchone()[0]

            while attempts < 6:
                otherwords = c.execute('select word from lemmas where word <> "{}";'.format(firstword)).fetchall()
                if len(otherwords) > 1:
                    s = soundex.Soundex()
                    phon = s.soundex(firstword)
                    results = set()
                    for w in otherwords:
                        if s.soundex(w[0]) == phon:
                            results.add(w)

                sentence_skeletons = ["According to Soundex, {} sounds like {}, {} and {}.",
                                      "Did you know that {} sounds like {}, {} and {}? At least Soundex thinks so.",
                                      "Soundex thinks {} sounds like {}, {} and {}.",
                                      "In Soundex English, {} sounds just like {}, {} and {}.",
                                      "Excuse me, did you say {}, {}, {} or {}? I tend to confuse those words. Just like Soundex."]

                if len(results) > 2:
                    word2 = random.sample(results, 1)[0]
                    results.remove(word2)
                    word3 = random.sample(results, 1)[0]
                    results.remove(word3)
                    word4 = random.sample(results, 1)[0]
                    results.remove(word4)
                    output = random.choice(sentence_skeletons).format(firstword, word2[0], word3[0], word4[0])
                    if len(output) < 141:
                        return output

                attempts += 1
        except TypeError:
            pass

def tweet_something(debug):
    api = login()
    output = stick_together_output("lemmas.sqlite")
    if debug:
        print(output)
    else:
        api.update_status(status=output)
        print(output)

tweeted = False
while not tweeted:
    try:
        tweet_something(False)
        tweeted = True
    except:
        pass

