import requests
import json
import logging
import sys
from twisper.config  import Config
from twisper.twitter_api import T_API
from time import sleep
from typing import Any

import tweepy
from twisper.loggers import setup_logging_pre

# check min. python version
if sys.version_info < (3, 8):  # pragma: no cover
    sys.exit("Twisper requires Python version >= 3.8")

# get logger
logger = logging.getLogger('twisper')

def main():
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    return_code: Any = 1

    try:
        setup_logging_pre()

        config = Config()

        logger = config.set_up_logger()

        api = T_API(config=config, log=logger)

        run = True

        tweets_engaged = 0
        errors_returned = 0
        epoch = 1

        while run:
            tweets_engaged = 0
            try:
                print(f'Starting epoch: {epoch}')
                # Search tweets
                tweet_list = api.search_tweets()

                # Process tweets
                for tweet in tweet_list:
                    # Validate tweet
                    if not api.validate_tweet(tweet):
                        continue
                    
                    # # Verify original
                    tweet = api.original_tweet(tweet)
                    if tweet is None:
                        continue

                    # Verify not using banned words
                    if api.is_banned_user(tweet):
                        continue

                    # Everything seems good, lets get to work
                    if api.engage(tweet):
                        tweets_engaged += 1
                    else:
                        errors_returned += 1
                
                epoch += 1
                logger.info(f'Finished analyzing (epoch {epoch}). Engaged with {tweets_engaged}/{str(len(tweet_list))} tweets.')
            except Exception as e:
                logger.error(str(e))
                sleep(100 * len(config.TAGS_SEARCH))

            sleep(2 * len(config.TAGS_SEARCH))

            if errors_returned > 1:
                print('something happened, exiting')
                run = False
    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    except Exception:
        logger.exception('Fatal exception!')
    finally:
        sys.exit(return_code)


if __name__ == "__main__":  # pragma: no cover
    main()