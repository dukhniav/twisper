import tweepy
from time import sleep
from typing import Any

import logging

from twisper.enums import TimerType
from twisper.config import Config

logger = logging.getLogger(__name__)

class T_API:
    def __init__(self, config: Config) -> None:
        self.auth =tweepy.OAuth1UserHandler(config.API_KEY,
                                    config.API_KEY_SECRET,
                                    config.ACCESS_TOKEN,
                                    config.ACCESS_TOKEN_SECRET) 

        self.twitter = tweepy.API(self.auth)
        self.config = config
        

    def get_friends(self) -> list:
        '''
        Get list of friends
        '''
        logger.info('Retreiving friends.')
        friend_list = self.twitter.get_friends()
        friends = [x.screen_name for x in friend_list]

        return friends        
    
    
    def retweet(self, id, dry_run) -> bool:
        '''
        Retweet
        '''
        status = True
        try:
            if dry_run:
                print(f'Retweeted {id}')
            else:
                status = self.twitter.retweet(id)
            logger.info(f'Retweeted {id}')

            self._sleep(TimerType.RETWEET)
        except Exception as e:
            status = False
            # In case the error contains sentences that mean the app is probably banned or the user over daily
            # status update limit, we cancel the function
            print(str(e))
            if "retweeted" not in str(e):
                logger.error(str(e))

        return status


    def like(self, id, dry_run) -> bool:
        '''
        So we don't skip the tweet if we get the "You have already favorited this status." error
        If the tweets contains any like_tags, it automatically likes the tweet
        '''
        status = True

        try:
            if dry_run:
                print("Liked: " + id)
            else:
                self.twitter.create_favorite(id)

            logger.info("Liked: " + str(id))
        except:
            status = False
            pass

        return status

    def send_message(self, author_id, username, msg_text, dry_run) -> bool:
        '''
        Sends DM to tweet author
        '''
        status = True

        if dry_run:
            print(f'Sent DM to {username}')
        else:
            try:
                self.twitter.send_direct_message(text=msg_text,recipient_id=author_id)
                logger.info(f'Sent DM to {username}')
                
                self._sleep(TimerType.MESSAGE)
            except:
                status = False
                pass
        
        return status


    def follow(self, username, dry_run) -> bool:
        '''
        If the tweet contains any follow_tags, it automatically follows all the users mentioned in the tweet (if there's any) + the author
        '''
        status = True

        if dry_run:
            print(f'Sent DM to {username}')
            logger.info(f'Sent DM to {username}')
        else:
            try:
                self.twitter.create_friendship(username)
                logger.info(f'Sent DM to {username}')

                sleep(TimerType.FOLLOW)
            except:
                pass
    
        return status


    def unfollow(self, screen_name) -> bool:
        '''
        Unfollow friend
        ''' 
        status = False
        try:
            self.twitter.destroy_friendship(screen_name)
            logger.info(f'Unfollowed @{screen_name}')

            status = True
        except Exception as e:
            print(e)
        
        return status


    def _sleep(self, timer_type):
        '''
        Sleep func based on who called it
        '''
        sleep_timer = 0

        if timer_type == TimerType.RETWEET:
            sleep_timer = self.config.TIMER_RT
        elif timer_type == TimerType.FOLLOW:
            sleep_timer = self.config.TIMER_FOLLOW
        elif timer_type == TimerType.MESSAGE:
            sleep_timer = self.config.TIMER_MSG
        else:
            logger.error('Wrong timer type received')
            sleep_timer = self.config.TIMER_SLEEP

        sleep(sleep_timer)


    def search_tweets(self, query, results, language) -> Any:
        '''
        Search for tweets
        '''
        return self.twitter.search_tweets(q=query, lang=language, include_rts=False,  count=results)