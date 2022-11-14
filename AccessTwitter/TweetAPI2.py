import json
import os
import requests
from requests.adapters import HTTPAdapter
import time
import datetime
from dotenv import load_dotenv
import urllib3

#if any questions, please ask HISADA.

class search_twitter():
    def __init__(self):
        load_dotenv('./.env')
        if not os.getenv('BearerToken') == None:
            self.BearerToken = os.getenv('BearerToken')
        else:
            raise Exception("Please set BearerToken")
        if not os.getenv('canaria') == None:
            self.canaria = os.getenv('canaria')
        else:
            self.canaria = ''
        self.post_header = {"Authorization":"Bearer {}".format(self.BearerToken)}
        self.status = 'unfinish'

    def savedata(self, data_dict, dirname = ''):
        for i in data_dict:
            if not self.canaria == '':
                if os.path.exists('/data1/' + self.canaria):
                    os.makedirs('/data1/'+self.canaria+'/'+dirname,exist_ok=True)
                for d in data_dict[i]:
                    with open('/data1/'+self.canaria+'/'+dirname+'/'+i+'.jsonl','a',encoding='utf8',errors='ignore') as td:
                        td.write(json.dumps(d,ensure_ascii=False)+'\n')
            else:
                os.makedirs(dirname,exist_ok=True)
                for d in data_dict[i]:
                    with open(dirname+'/'+i+'.jsonl','a',encoding='utf8',errors='ignore') as td:
                        td.write(json.dumps(d,ensure_ascii=False)+'\n')
        return 'written'

    def set_continue_error(self, keyword, next_token, method):
        with open('error_check.jsonl', 'w', encoding='utf8', errors='ignore') as td:
            td.write(json.dumps({'query':keyword,'next_token':next_token,'Method':method,'Date': datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}, ensure_ascii=False) + '\n')

    def full_search_tweet(self, keyword, dirname='', start_day='', end_day=7, next_token = ''):
        method = 'full_search'
        if start_day == '':
            start_day = datetime.datetime.now() - datetime.timedelta(days=7)
        def construct_request(keyword, next_token, start_time='', end_time=''):
            SearchURL = 'https://api.twitter.com/2/tweets/search/all'
            params = {'query': keyword,
                      'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id',
                      'max_results': 500,
                      'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics',
                      'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
                      'poll.fields': 'duration_minutes,end_datetime,id,options,voting_status',
                      'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                      'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                      }
            if next_token != '':
                params['next_token'] = next_token
            if start_time != '':
                params['start_time'] = start_time
            if end_time != '':
                params['end_time'] = end_time
            return SearchURL, params

        if dirname == '':
            if len(keyword) < 5:
                dirname = 'query_'+ keyword
            else:
                dirname = 'query_'+ keyword[0:5]

        for day in range(end_day):
            start_time = (start_day.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=day) - datetime.timedelta(hours=9)).isoformat() + 'Z'
            end_time = (start_day.replace(hour=23, minute=59, second=59, microsecond=99) + datetime.timedelta(days=day) - datetime.timedelta(hours=9)).isoformat() + 'Z'
            dir = dirname + '/'+(start_day+ datetime.timedelta(days=day)).date().isoformat()+'/'
            while True:
                url, params = construct_request(keyword, next_token=next_token, start_time=start_time, end_time=end_time)
                data, next_token, res_header = self.send_request(url, params)
                if len(data) < 1:
                    break
                self.savedata(data, dir)
                self.set_continue_error(keyword,next_token,method)
                if next_token == '':
                    break
                self.check_rate_limit(res_header)
                if next_token == '' or next_token == 'invalid_query':
                    break
            if next_token == 'invalid_query':
                break
        if next_token == 'invalid_query':
            self.status = 'invalid_query'
        else:
            self.status = 'finish'

    def checkid(self,username):
        endpoint = 'https://api.twitter.com/2/users/by/username/'
        response = requests.get(endpoint+username,
                                 headers=self.post_header,
                                timeout=3.5
                                )
        id = response.json()['data']['id']
        return id

    def user_timeline(self, userid, dirname='', next_token=''):
        method = 'timeline'
        if not userid.isdigit():
            userid = self.checkid(userid)

        def construct_request(keyword, next_token):
            SearchURL = 'https://api.twitter.com/2/users/{}/tweets'.format(keyword)
            params = {
                'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
                'max_results': 100,
                'media.fields': 'duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics',
                'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
                'poll.fields': 'duration_minutes,end_datetime,id,options,voting_status',
                'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                }
            if next_token != '':
                params['pagination_token'] = next_token
            return SearchURL, params

        if dirname == '':
            dirname = userid + '/timeline'
        else:
            dirname = dirname + '/' + userid + '/timeline'

        while True:
            url, params = construct_request(userid, next_token=next_token)
            data, next_token, res_header =self.send_request(url, params)
            if len(data) < 1:
                break
            self.savedata(data, dirname)
            self.set_continue_error(userid, next_token, method)
            if next_token == '':
                break
            self.check_rate_limit(res_header)
            if next_token == '' or next_token == 'invalid_query':
                break

    def retweetedby(self, tweetid, dirname='', next_token = ''):
        method = 'retweetedby'
        def construct_request(keyword, next_token):
            SearchURL = 'https://api.twitter.com/2/tweets/{}/retweeted_by'.format(keyword)
            params = {
                'max_results': 100,
                'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
            }
            if next_token != '':
                params['pagination_token'] = next_token
            return SearchURL, params
        if dirname == '':
            dirname = tweetid + '/retweets'
        else:
            dirname = dirname + '/' + tweetid + '/retweets'

        while True:
            url, params = construct_request(tweetid, next_token=next_token)
            data, next_token, res_header =self.send_request(url, params)
            if len(data) < 1:
                break
            self.savedata(data, dirname)
            self.set_continue_error(tweetid, next_token, method)
            if next_token == '':
                break
            self.check_rate_limit(res_header)
            if next_token == '' or next_token == 'invalid_query':
                break

    def follow_follower(self, userid, friends='both', dirname='',length = -1, next_token = ''):
        if not userid.isdigit():
            userid = self.checkid(userid)

        def construct_request_follow(keyword, next_token):
            SearchURL = 'https://api.twitter.com/2/users/{}/following'.format(keyword)
            params = {
                'max_results': 1000,
                'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
            }
            if next_token != '':
                params['pagination_token'] = next_token
            return SearchURL, params
        def construct_request_follower(keyword, next_token):
            SearchURL = 'https://api.twitter.com/2/users/{}/followers'.format(keyword)
            params = {
                'max_results': 1000,
                'tweet.fields': 'attachments,author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld',
                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
            }
            if next_token != '':
                params['pagination_token'] = next_token
            return SearchURL, params

        if not friends == 'follower':
            counter = 0
            if dirname == '':
                dirname = userid + '/follow'
            else:
                dirname = dirname + '/' + userid + '/follow'
            method = 'follow'
            while True:
                url, params = construct_request_follow(userid, next_token=next_token)
                data, next_token, res_header = self.send_request(url, params)
                if len(data) < 1:
                    break
                self.savedata(data, dirname)
                self.set_continue_error(userid, next_token, method)
                self.check_rate_limit(res_header)
                if next_token == '':
                    break
                if length > 0 and counter > length:
                    break
                else:
                    counter += 1
                if next_token == '' or next_token == 'invalid_query':
                    break
        elif not friends == 'follow':
            counter = 0
            if dirname == '':
                dirname = userid + '/follower'
            else:
                dirname = dirname + '/' + userid + '/follower'
            method = 'follower'
            while True:
                url, params = construct_request_follower(userid, next_token=next_token)
                data, next_token, res_header = self.send_request(url, params)
                if len(data) < 1:
                    break
                self.savedata(data, dirname)
                self.set_continue_error(userid, next_token, method)
                self.check_rate_limit(res_header)
                if next_token == '':
                    break
                if length > 0 and counter > length:
                    break
                if next_token == '' or next_token == 'invalid_query':
                    break

    def send_request(self, URL, params):
        session = requests.Session()
        retries = urllib3.util.Retry(total=5,  # リトライ回数
                        backoff_factor=900,  # sleep時間
                        status_forcelist=[500, 502, 503, 504, 404])

        session.mount("https://", HTTPAdapter(max_retries=retries))
        time.sleep(1)
        response = session.get(URL,
                            params=params,
                            headers=self.post_header,
                            timeout=(3.0, 7.5))

        if response.status_code == 200:
            tweets = response.json()
            next_token = ''
            response_data = {}
            if 'meta' in tweets:
                if 'next_token' in tweets['meta']:
                    next_token = tweets['meta']['next_token']
                if 'result_count' in tweets['meta']:
                    if tweets['meta']['result_count'] == 0:
                        return {}, next_token, response.headers
            if 'data' in tweets:
                response_data['data'] = tweets['data']
            if 'includes' in tweets:
                if 'users' in tweets['includes']:
                    response_data['users'] = tweets['includes']['users']
                if 'media' in tweets['includes']:
                    response_data['media'] = tweets['includes']['media']
                if 'places' in tweets['includes']:
                    response_data['places'] = tweets['includes']['places']
                if 'tweets' in tweets['includes']:
                    response_data['conversation'] = tweets['includes']['tweets']

            return response_data, next_token, response.headers

        elif response.status_code != 200:
            print('status_code:', response.status_code)
            return {}, '', response.headers

    def check_rate_limit(self, header):
        if 'x-rate-limit-remaining' in header and 'x-rate-limit-reset' in header:
            remain = int(header['x-rate-limit-remaining'])
            reset = int(header['x-rate-limit-reset'])
            now = datetime.datetime.now().timestamp()
            wait_time = reset - now
            if remain < 2:
                print('sleep:', wait_time)
                time.sleep(wait_time)
        else:
            time.sleep(60)

if __name__ == '__main__':
    start_time = datetime.datetime(2022, 11, 2, hour=0, minute = 0,second = 0)
    #search_twitter().full_search_tweet('retweets_of_tweet_id:1581987544777883648')
    #search_twitter().full_search_tweet('混雑',start_day=start_time, end_day=1)
    #search_twitter().full_search_tweet('point_radius:[138.46877332901622 35.02008284207412 2km]','清水', start_day=start_time)
    #search_twitter().retweetedby('1578172221310521344')
    #search_twitter().follow_follower('ProfMatsuoka',friends='follow')