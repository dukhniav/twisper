import tweepy
import random 
from datetime import datetime, timezone
from time import sleep

from logging import Logger

from config import Config

class T_API:
    def __init__(self, config: Config, log: Logger) -> None:
        self.auth =tweepy.OAuth1UserHandler(config.API_KEY,
                                    config.API_KEY_SECRET,
                                    config.ACCESS_TOKEN,
                                    config.ACCESS_TOKEN_SECRET) 

        self.log = log
        self.api = tweepy.API(self.auth)
        self.config = config
        self.dry_run = self.config.DRY_RUN
        if self.dry_run:
            self.log.warning(f'Bot is in DRY MODE, all actions simulated!')
        else:
            self.log.warning('Bot is in LIVE mode, all actions are for realzies!')

        self.banned_users = self.config.BANNED_USERS
        self.banned_name_keywords = self.config.BANNED_NAME_KEYWORDS
        self.last_rt = datetime.now(timezone.utc)
        self.friend_count = 0
        self.friends = self.get_friends()


    def get_friends(self) -> list:
        '''
        Get list of friends
        '''
        self.log.info('Retrieving friends')
        friend_list = self.api.get_friends()
        friends = [x.screen_name for x in friend_list]
        self.log.info("Friends retrieved successfully!")
       
        # sleep(self.config.TIMER_FOLLOW)
        return friends        
    

    def engage(self, tweet) -> bool:
        '''
        Retweets a tweet.

        This is ran under a try clause because there's always an error when trying to retweet something
        already retweeted. So if that's the case, the except is called and we skip this tweet
        If the tweet wasn't retweeted before, we retweet it and check for other stuff

        Checks if RT/DM/follow/like are required
        '''
        sleep(self.config.TIMER_RT)
        rt_status = False

        rt_tags = dm_tags = fl_tags = []

        if any(x in tweet.text.lower() for x in self.config.TAGS_RT):
            rt_tags = [i for i in self.config.TAGS_RT if i in tweet.text.lower().split()]
            rt_status = self.retweet(tweet)
        if any(x in tweet.text.lower() for x in self.config.TAGS_MSG):
            dm_tags = [i for i in self.config.TAGS_MSG if i in tweet.text.lower().split()]
            self.send_message(tweet.author_id)
        if any(x in tweet.text.lower() for x in self.config.TAGS_FOLLOW):
            fl_tags = [i for i in self.config.TAGS_FOLLOW if i in tweet.text.lower().split()]
            self.follow(tweet)


        self.log_tweet(tweet, rt_tags, dm_tags, fl_tags)

        return rt_status
            

    def is_banned_user(self, tweet):
        '''
        Check if the tweet author is banned
        '''
        if tweet.user.screen_name.lower() in self.banned_users or any(x in tweet.user.name.lower() for x in self.banned_name_keywords):
            # If it's the original one, we check if the author is banned
            self.log.info("Avoided user with ID: " + tweet.user.screen_name + " & Name: " + tweet.user.name)
            return True
        return False


    def get_original(self, tweet):
        '''
        Possibly recursive function to get original tweet
        '''
        pass

    def original_tweet(self, tweet):
        '''
        Check if tweet is a retweet, if so, find original tweet
        '''
        if tweet.retweeted_status is not None:
            # In case it is a retweet, we switch to the original one
            if any(x in tweet.retweeted_status.text.lower().split() for x in self.config.TAGS_RT):
                tweet = tweet.retweeted_status
            else:
                tweet = None
                
        return tweet

    def log_tweet(self, tweet, rt_tags, dm_tags, fl_tags):
        print('logging tweet')

        file1 = open('myfile.txt', 'a')
        seperator = '==========================================================================='
        mini_sep = '======================'
        date = tweet.created_at
        user = tweet.username
        screenname = tweet.screenname
        tweet_text = tweet.text

        string = f'''
            {date}  --  username={user}  -//- screenname={screenname} \n 
            {mini_sep} \n
            RT_TAGS={rt_tags} \n
            FL_TAGS={fl_tags} \n
            DM_TAGS={dm_tags} \n
            {mini_sep} \n
            {tweet_text} \n
            {seperator} \n\n
        ''' 
        
        print(string)
        # Writing multiple strings
        # at a time
        file1.writelines(string)
        
        # Closing file
        file1.close()


    def retweet(self, tweet):
        '''
        Retweet
        '''
        try:
            # Retweet
            if self.dry_run:
                print(f'Retweeting: {tweet.id}')
            else:
                status = self.api.retweet(tweet.id)
            self.log.info(f'Retweeted {tweet.id} ... {status}')

        except Exception as e:
            # In case the error contains sentences that mean the app is probably banned or the user over daily
            # status update limit, we cancel the function
            print(str(e))
            if "retweeted" not in str(e):
                self.log.error(str(e))
                return False
        return True


    def like(self, tweet):
        '''
        So we don't skip the tweet if we get the "You have already favorited this status." error
        If the tweets contains any like_tags, it automatically likes the tweet
        '''
        try:
            if self.dry_run:
                print(f'Liking tweet {tweet.id}')
            else:
                self.api.create_favorite(tweet.id)
            self.log.info("Liked: " + str(tweet.id))
        except:
            pass

    def send_message(self, author_id, username):
        '''
        Sends DM to tweet author
        '''
        try:
            # So we don't skip the tweet if we get the "You cannot send messages to users who are not following you." error
            if self.config.ALLOW_CONTACT:
                msg_text = self.config.MSG_TEXT[random.randint(0, len(self.config.MSG_TEXT) - 1)]
                # If the tweet contains any of the message_tags, we send a DM to the author with a random
                # sentence from the message_text list
                if self.dry_run:
                    print(f'Sending DM to @{author_id}: {msg_text}')
                else:
                    self.api.send_direct_message(text=msg_text,recipient_id=author_id)
                
                self.log.info(f'Sent DM to {username}')
                # 1 every 86.4s guarantees we won't pass the 1000 DM per day limit
                sleep(self.config.TIMER_MSG)
        except:
            pass

    def follow(self, tweet):
        '''
        If the tweet contains any follow_tags, it automatically follows all the users mentioned in the tweet (if there's any) + the author
        '''
        addFriends = []
        
        friends_count = len(self.friends)
        
        if tweet.username not in self.friends:
            if self.dry_run:
                print(f'Following @{tweet.username}')
            else:
                self.api.create_friendship(tweet.username)
            
            self.log.info(f'Followed: @{tweet.username}')

            addFriends.append(tweet.username)
            
            sleep(self.config.TIMER_FOLLOW - self.config.TIMER_RT if self.config.TIMER_FOLLOW > self.config.TIMER_RT else 0)

        for name in tweet.mentioned_user_ids:
            if name.username in self.friends or name.username in addFriends:
                continue

            if self.dry_run:
                print(f'Following mentioned @{name.username}')
            else:
                self.api.create_friendship(name.username)
            self.log.info(f'Followed mentioned @{name.username}')

            addFriends.append(name.username)

            sleep(self.config.TIMER_RT)

        # Check if need to unfollow someone
        self.unfollow()


    def unfollow(self, friends_count, potential_friends) -> None:
        '''
        Twitter sets a limit of not following more than 2k people in total (varies depending on followers)
        So every time the bot follows a new user, its deletes another one randomly
        '''        
        if friends_count + len(potential_friends) >= self.config.FOLLOW_LIMIT:
            self.log.info('At follow cap, unfollowing some folks.')
            while friends_count < self.api.get_user().friends_count:
                try:
                    x = self.friends[random.randint(0, len(self.friends) - 1)]

                    self.log.info(f'Unfollowed: @{x}')

                    if self.dry_run:
                        print(f'Unfollowing @{x}')
                    else:
                        self.api.destroy_friendship(screen_name=x)
                    self.friends.remove(x)
                    self.log.info(f'Unfollowed @{x}')
                except Exception as e:
                    print(e)
        self.friends.extend(potential_friends)


    def validate_tweet(self, tweet) -> bool: 
        '''
        Validates tweet.
        '''
        valid_words = True

        # Check for banned words
        for word in self.config.BANNED_KEYWORDS:
            if (tweet.text.lower().find(word) != -1):
                valid_words = False
                break

        # Check date is within config
        valid_date = valid_words and self.tweet_date_valid(tweet)

        # Check if tweet requires retweeting
        valid_rt_count = valid_date and self.tweet_established(tweet)

        # Check if retweet is required        
        rt_required = valid_rt_count and self.is_rt_required(tweet)

        return rt_required
    

    def is_rt_required(self, tweet) -> bool:
        ''' 
        Check if tweet needs to be retweeted. 
        Only care about the ones that do.
        '''

        return any(x in tweet.text.lower().split() for x in self.config.TAGS_RT)
        

    def search_tweets(self):
        '''
        Search for tweets
        '''
        searched_tweets = []

        for tag in self.config.TAGS_SEARCH:
            searched_tweets += self.api.search_tweets(q=tag, lang='en', include_rts=False,  count=self.config.MAX_RESULTS)

        self.api.search_geo
        return searched_tweets


    def tweet_established(self, tweet) -> bool:
        '''
        Checks if tweet already has more than configured retweets
        '''
        return tweet.retweet_count >= self.config.MIN_RT_COUNT


    def tweet_date_valid(self, tweet):
        '''
        Checks the age of tweet
        '''
        # get tweet publish date
        tweet_date = tweet.created_at

        # get current date and time
        now = datetime.now(timezone.utc)

        return int((now-tweet_date).days) <= self.config.MAX_AGE
