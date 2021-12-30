"""
LOGURU DOCS:      https://loguru.readthedocs.io/en/stable/
LOGURU SOURCE:    https://github.com/Delgan/loguru

"""
from os import system
from time import sleep
from sys import stderr
from loguru import logger

class Progress:
    '''Class used for logging.'''

    format_stderr_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '
    format_file_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '

    def i(message):
        logger.remove()
        logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format=Progress.format_file_log, level='INFO')
        logger.add(stderr, format=Progress.format_stderr_log, level='INFO')
        logger.info(message)

    def s(message):
        logger.remove()
        logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format=Progress.format_file_log, level='SUCCESS')
        logger.add(stderr, format=Progress.format_stderr_log, level='SUCCESS')
        logger.success(message)

    def w(message):
        logger.remove()
        logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format= Progress.format_file_log, level='WARNING')
        logger.add(stderr, format=Progress.format_stderr_log, level='WARNING')
        logger.warning(message)

    def e(message):
        logger.remove()
        logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format= Progress.format_file_log, level='ERROR')
        logger.add(stderr, format=Progress.format_stderr_log, level='ERROR')
        logger.error(message)

    # use for logging symbol, buy, sell price for easy parsing
    def crit(message):
        logger.remove()
        logger.add('LOGS/CRIT_art_{time:DD-MMM-YYYY}.log', format= Progress.format_file_log, level='CRITICAL')
        logger.add(stderr, format=Progress.format_stderr_log, level='CRITICAL')
        logger.critical(message)

    # use to log buy and sell JSON data, FILE ONLY
    def debug(message):
        logger.remove()
        logger.add('LOGS/DEBUG_art_{time:DD-MMM-YYYY}.log', format= Progress.format_file_log, level='DEBUG')
        logger.debug(message)

    # use to log profit/loss from each buy/sell combo
    def trace(message):
        logger.remove()
        logger.add('LOGS/TRACE_art_{time:DD-MMM-YYYY}.log', format= Progress.format_file_log, level='TRACE')
        logger.add(stderr, format=Progress.format_stderr_log, level='TRACE')
        logger.trace(message)

    # writes to stderr slowly
    def slowly(msg):
        for c in msg +'\n':
            stderr.write(c)
            stderr.flush()
            sleep(1./20)

    # clear the CLI
    def clearly():
        _ = system('clear')