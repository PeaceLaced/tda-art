"""
LOGURU DOCS:      https://loguru.readthedocs.io/en/stable/
LOGURU SOURCE:    https://github.com/Delgan/loguru

"""
from os import system
from time import sleep
from sys import stderr
from loguru import logger
from enum import Enum

class ProgressReportException(TypeError):
    '''Raised when there are issues with the progress report API.'''

class ProgressType(Enum):
    INFO = 'INFO'
    SUCCESS = 'SUCCESS'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRIT = 'CRIT'
    DEBUG = 'DEBUG'
    TRACE = 'TRACE'
    
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
        
##### TODO: add 'raise exception' and log select functionality
def report_config(config_file, config_variables, log_select=ProgressType.WARNING, report_config=False):
    '''takes a list of variables from the config file, reports them to the log
    
    :param config_file: file name string
    :param config_variables: list of variables from a config file to report
    :param log_select: default is WARNING log. Any progress report log is valid.
    '''
    if not isinstance(config_file, str):
        raise ProgressReportException('config_file must be a string')
        
    if not isinstance(config_variables, list):
        raise ProgressReportException('config_variables must be a list')
        
    if not isinstance(log_select, ProgressType):
        raise ProgressReportException('log_select must be of type ProgressType')
        
    # TODO: allow reporting to other logs <>
    if report_config:
        [Progress.w('(' + str(config_file) + ')_(' + str(c_variable) + ')') for c_variable in config_variables]
            
        
        


