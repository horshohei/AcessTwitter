必要なもの

pip install requests
Twitter API Bearer Token (Acacdemic推奨)

実行ディレクトリに.envファイルを作り
BearerToken = 'AAAAAAAAAAAAAA'
を書いてください
またカナリアで動かすときは
canaria = 'account_name'でData1フォルダにある自分の保存フォルダの名前を入力すると、そちらにデータが保存されます。
これは環境変数読み込んでいるので
export BearerToken = 'AAA'でもいけると思います

使い方

from TweetAPI2 import search_twitter()

共通仕様
データの保存はdata.jsonlにメインのデータ
1行に1ツイートなどが入ります。
エンドポイントによってはuser.jsonlやmedia.jsonl、Conversation.jsonlが生成されます。
userは検索したツイートのユーザ情報が含まれます
Mediaはツイートに含まれる画像や映像のデータが含まれています。
Conversation.jsonlはツイートがリプライや引用リツイートのとき、その元のツイートや会話のツリーなどの情報が含まれています。

かくメソッドにはnext_tokenという引数を設けています。これはなにかのエラーやネット関係のトラブルでプログラムが停止した際に、最後収集終わった地点から次の情報を示しています。
どこまで終わったかわからなくなることが多いので設けています。error_check.jsonlというファイルが勝手に生成されます。そこに、途中まで実行していた内容が書き込まれていますので、再開する際に自分で指定すれば、いちからやり直しを避けることができます。

1.full_search_tweet(keyword,dirname,start_day,end_day,next_token='')
クエリを用いてTwitterの全期間データを検索できます
必須
keyword:クエリです。:String

東京 隅田川　で東京と隅田川のAND検索です
東京 OR 埼玉　で東京と埼玉のOR検索です
(東京 OR 埼玉) 隅田川　で隅田川と東京か埼玉のどちらかを含むTweetを検索できます。

また
url:"https://hogehoge/" でURLを含むツイートを検索できます。

conversation_id:123456 でconversation_idが振られたツイートを検索できます。

詳しくはTwitterの
https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
参照

Option仕様:
dirname:String
保存ファイルは、デフォルトでは実行フォルダにquery_{クエリの5文字目まで}/日付/デタ等
の形で保存していきます。
保存フォルダを指定するときはdirnameにディレクトリ名を指定してくださいその場合は　指定名/日付/デタ等の構造になります。　絶対パスでも動くと思います。

startday:Datetime
検索開始の日付を指定してください、その際にはdatetimeをつかって
start_time = datetime.datetime(2022, 7, 10, hour=0, minute = 0,second = 0)
のような形で指定してください
何も書かなければ、7日前になります
勝手にJSTに変換した時間で検索しています。入力時に補正は必要ないです

end_day:Integer
検索期間の長さを指定してください。
一日ごとに分けて検索かけるので、何日でもOKです。今日を超えるとやがて止まります

user_timeline(self, userid, dirname='', next_token=''):
ユーザのタイムラインを検索します。
必須：Userid：String
ユーザーIDとなっていますが、@から始まるユーザ名でも問題ないですが、全部数値のユーザ名があると多分バグります
基本的には'author_id'で取得できる数値列を入力する形になります。

Option仕様:
dirname:String
保存ファイルは、デフォルトでは実行フォルダにUserID/timeline/デタ等
の形で保存していきます。
保存フォルダを指定するときはdirnameにディレクトリ名を指定してくださいその場合は　指定名/UserID/timeline/デタ等の構造になります。

retweetedby(self, tweetid, dirname='', next_token = ''):
あるツイートにリツイートしたユーザの情報を取得します。　リツイートした時間はわからない仕様だったと思います。
必須：Tweetid:String
ツイートのIDを入力してください
個別のツイートを開いたときの最後の数字列です
保存ファイルは、デフォルトでは実行フォルダにTweetID/retweets/デタ等
の形で保存していきます。
保存フォルダを指定するときはdirnameにディレクトリ名を指定してくださいその場合は　指定名/TweetID/retweets/デタ等の構造になります。

follow_follower(self, userid, friends='both', dirname='', next_token = ''):
あるユーザのフォローとフォロワーリストを作ります
必須：USERID：STRING
取得したいユーザのIDを入力してください。@から始まるユーザ名でも問題ないですが、全部数値のユーザ名があると多分バグります


Option仕様:
dirname:String
保存ファイルは、デフォルトでは実行フォルダにUserID/follow(follower)/デタ等
の形で保存していきます。
保存フォルダを指定するときはdirnameにディレクトリ名を指定してくださいその場合は　指定名/UserID/follow(follower)/デタ等の構造になります。

frinends: 'follow' or 'follower' or 'both'
フォローかフォロワーリストのどちらかだけ取得したい場合はfollowまたはfollowerを引数に与えてください
なお、しようとしてフォローリストから取得します。


To do
アカデミックアカウントないときでも使えるやつと、ツイート１つを見つけてくるやつ
