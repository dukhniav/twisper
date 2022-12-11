"""
   ___                 __  _
  / __\  ___   _ __   / _|(_)  __ _
 / /    / _ \ | '_ \ | |_ | | / _` |
/ /___ | (_) || | | ||  _|| || (_| |
\____/  \___/ |_| |_||_|  |_| \__, |
                              |___/
"""

import json
import logging 

CONFIG = 'config.json'

class Config:
    def __init__(self) -> None:
        with open(CONFIG,'r') as file:
            data = json.load(file)

        self.log_file = 'log.log'

        self.friend_file = 'data/friends.txt'
        


        # Config sections
        credentials = data['credentials']
        bot = data['bot_config']
        notifications = data['notification_config']
        contact = data['contact_config']
        search = data['search_config']
        banned = data['banned_config']
        timers = data['timer_config']

        ### DRY RUN ONLY - no retweets/follows/DMS
        self.DRY_RUN = bot['dry_run']

        # Don't start the bot if friends weren't correctly retrieved
        self.wait_retrieve = False

        '''
        Credentials
        '''
        self.API_KEY = credentials['api_key']
        self.API_KEY_SECRET = credentials['api_key_secret']
        self.BEARER_TOKEN = credentials['bearer_token']
        self.ACCESS_TOKEN = credentials['access_token']
        self.ACCESS_TOKEN_SECRET = credentials['access_token_secret']

        '''
        Bot config
        '''
        self.MAX_RESULTS = bot['max_results']
        self.FOLLOW_LIMIT = bot['follow_limit']
        self.MAX_AGE = bot['max_tweet_age'] # days
        self.MIN_RT_COUNT = bot['min_retweet_count']
        self.HEARTBEAT_INTERVAL = bot['heartbeat_interval']

        '''
        Notification config
        '''
        # Enable this if you want the bot to send a DM in case it detects any message_tags
        self.NOTIFY =   notifications['notify']
        self.NOTIFY_USERNAME = notifications['notify_username']

        '''
        Contacting
        '''
        # Enable this if you want the bot to send a DM in case it detects any message_tags
        self.ALLOW_CONTACT = contact['allow_contact']
        # These are supposed to be random msgs the bot would send if DMing is required
        self.MSG_TEXT = contact['msg_text']

        '''
        Search config
        ''' 
        # Twitter search config
        # DON'T WRITE ANYTHING IN CAPS, AS THE BOT AUTOMATICALLY FLATTERS ALL INPUT TEXTS. THUS ANY WORD WITH CAPS WON'T BE RECOGNIZED
        # Tags that Twitter will use to look up our tweets. Really important as all the script will be based on them
        self.TAGS_SEARCH  = search["tags_search" ]
        # What words will the bot check in order to retweet a tweet. It's important because if the bot doesnt
        # recognize any, it will skip the whole tweet and it wont check if it has to like, msg, or follow
        self.TAGS_RT  = search["tags_retweet"]
        # What words will trigger to send the author a DM with a random message_text
        self.TAGS_MSG = search["tags_message"]
        # What words will the bot check in order to follow the author of the tweet plus all the users mentioned in the text
        # (we assume that a retweet tag was recognized)
        self.TAGS_FOLLOW = search["tags_follow"]
        # What words will the bot look for in order to like a tweet (it also needs to contain a retweet tag)
        self.TAGS_LIKE = search["tags_like"]

        '''
        Banned config
        '''
        #Ignore tweets that contain any of these words
        self.BANNED_KEYWORDS =banned["keywords"]
        # Add to this list all the users whose contests (actually tweets that contain retweet_tags keywords) the script will
        # always skip (this is for the user's username, not name!) (username is the @ one)
        # Variables related to avoiding users don't need to have a value
        self.BANNED_USERS = banned["users" ]
        # Same but but in this case applied to the author's name
        self.BANNED_NAME_KEYWORDS = banned["name_keywords" ]

        '''
        Timer config
        '''
        # SLEEP means how long it'll have to wait to loop again after checking all tweets
        self.TIMER_SLEEP =timers["sleep_timer"]
        # How long to wait to pass to next tweet + follow_rate or dm_rate if it has to follow or dm someone
        #   from twitter docs -> rate limit is 300 per 3 hours = 36 seconds
        #   adding 1 second to be safe
        self.TIMER_RT=timers["rt_timer"] + 1
        # How long to wait after messaging someone. Just the diff between its value and retweet_rate's is added
        self.TIMER_MSG=timers["msg_timer" ]
        # How long to wait after following someone. 1st time the diff is added, afterwards the entire rate is added to the sleep
        self.TIMER_FOLLOW=timers["follow_timer"]
    
    def set_up_logger(self):
        #logging.basicConfig(format='%(asctime)s : %(levelname)s: %(message)s', 
                            # filename=self.log_file, filemode='w', 
                            # level=logging.INFO)

        logger = logging.getLogger(__name__)

        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        
        return logger
