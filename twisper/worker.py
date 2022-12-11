import logging 
import time
from os import getpid

from typing import Any, Optional, Callable

from twisper import __version__
from twisper.config import Config
from twisper.enums import RunMode, State
from twisper.twisper import TwisperBot

# get logger
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, config: Config) -> None:
        """
        Init all variables and objects the bot needs to work
        """
        logger.info(f"Starting worker {__version__}")

        self._config = config
        self._heartbeat_msg: float = 0
        self._heartbeat_interval = self._config.HEARTBEAT_INTERVAL

        self.twisper = TwisperBot(self._config)


    def run(self) -> None:
        state = None
        while True:
            state = self._worker(old_state=state)


    def start_up(self) -> None:
        pass


    def _worker(self, old_state: Optional[State]) -> State:
        """
        The main routine that runs each throttling iteration and handles the states.
        :param old_state: the previous service state from the previous call
        :return: current service state
        """
        state = self.twisper.state

        # Log state transition
        if state != old_state:
            logger.info(
                f"Changing state{f' from {old_state.name}' if old_state else ''} to: {state.name}")

            if state == State.STOPPED:
                # TODO: check if there is anything mid process
                pass

            if state == State.RUNNING:
                self.start_up()

            # Reset heartbeat timestamp to log the heartbeat message at
            # first throttling iteration when the state changes
            self._heartbeat_msg = 0


        elif self.state == State.RUNNING:
            # Use an offset of 1s to ensure a new candle has been issued
            self._throttle(throttle_secs=self._config.TIMER_SLEEP)

        if self._heartbeat_interval:
            now = time.time()
            if (now - self._heartbeat_msg) > self._heartbeat_interval:
                version = __version__
                logger.info(f"Bot heartbeat. PID={getpid()}, "
                            f"version='{version}', state='{state.name}'")
                self._heartbeat_msg = now

        return state


    def _throttle(self, throttle_secs: float):
        """
        Throttles the given callable that it
        takes at least `min_secs` to finish execution.
        :param throttle_secs: throttling interation execution time limit in seconds
        :return: Any (result of execution of func)
        """
        last_throttle_start_time = time.time()
        logger.debug("========================================")
        time_passed = time.time() - last_throttle_start_time
        sleep_duration = throttle_secs - time_passed
        sleep_duration = max(sleep_duration, 0.0)

        logger.debug(f"Sleeping for {sleep_duration:.2f} s, "
                     f"last iteration took {time_passed:.2f} s.")
        self._sleep(sleep_duration)


    @staticmethod
    def _sleep(sleep_duration: float) -> None:
        """Local sleep method - to improve testability"""
        time.sleep(sleep_duration)

    def exit(self) -> None:
        pass



    # def run():
    #     """
    #     This function will initiate and start bot.
    #     :return: None
    #     """

    #     return_code: Any = 1

    #     try:
    #         setup_logging_pre()

    #         config = Config()

    #         logger = config.set_up_logger()

    #         api = T_API(config=config, log=logger)

    #         run = True

    #         tweets_engaged = 0
    #         errors_returned = 0
    #         epoch = 1

    #         while run:
    #             tweets_engaged = 0
    #             try:
    #                 print(f'Starting epoch: {epoch}')
    #                 # Search tweets
    #                 tweet_list = api.search_tweets()

    #                 # Process tweets
    #                 for tweet in tweet_list:
    #                     # Validate tweet
    #                     if not api.validate_tweet(tweet):
    #                         continue
                        
    #                     # # Verify original
    #                     tweet = api.original_tweet(tweet)
    #                     if tweet is None:
    #                         continue

    #                     # Verify not using banned words
    #                     if api.is_banned_user(tweet):
    #                         continue

    #                     # Everything seems good, lets get to work
    #                     if api.engage(tweet):
    #                         tweets_engaged += 1
    #                     else:
    #                         errors_returned += 1
                    
    #                 epoch += 1
    #                 logger.info(f'Finished analyzing (epoch {epoch}). Engaged with {tweets_engaged}/{str(len(tweet_list))} tweets.')
    #             except Exception as e:
    #                 logger.error(str(e))
    #                 sleep(100 * len(config.TAGS_SEARCH))

    #             sleep(2 * len(config.TAGS_SEARCH))

    #             if errors_returned > 1:
    #                 print('something happened, exiting')
    #                 run = False
    #     except SystemExit as e:  # pragma: no cover
    #         return_code = e
    #     except KeyboardInterrupt:
    #         logger.info('SIGINT received, aborting ...')
    #         return_code = 0
    #     except Exception:
    #         logger.exception('Fatal exception!')
    #     finally:
    #         sys.exit(return_code)


