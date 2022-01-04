"""
- (main_strat_random.py)

"""

from time import sleep
from random import randrange
from tda.client import synchronous

# slowly converting everyting to the new API
from z_art.progress_report.api_progress_report import report_config
from z_art.progress_report.api_progress_report import Progress as progress

from z_art.strategy_select.api_strat_select import OrderType
from z_art.strategy_select.api_strat_select import data_syndicate
from z_art.strategy_select.api_strat_select import order_get_details
from z_art.strategy_select.api_strat_select import order_place_equity_market

class RandomStratTypeException(TypeError):
    '''Raised when there is a type error in :meth:`run_random_strat`.'''
    
class RandomStratValueException(ValueError):
    '''Raised when there is a value error in :meth:`run_random_strat`.'''
    
def run_strat_random(tda_client, stocks_to_trade):
    '''
    Randomly trade stocks by defining constants below.
    - The RANDOM strat takes a list and randomly selects one stock,
      buys, holds, sells, repeats.
     CAUTION: this strat never wins
    
    :param tda_client: The client object created by tda-api.

    '''
    
    if not isinstance(tda_client, synchronous.Client):
        raise RandomStratTypeException('tda client object is required')
        
    if not isinstance(stocks_to_trade, list):
        raise RandomStratTypeException('stocks_to_trade must be a list')

    TRADE_CYCLE_DEFAULT_R = 330
    TRADE_CYCLES_R = 330
    SHARE_QUANTITY = 1
    HOLD_STOCK_THIS_LONG = 50
    WAIT_BEFORE_BUYING_AGAIN = 10
    STOP_TRYING_TO_BUY = 10
    
    config_variables = [TRADE_CYCLE_DEFAULT_R, TRADE_CYCLES_R, SHARE_QUANTITY, HOLD_STOCK_THIS_LONG, WAIT_BEFORE_BUYING_AGAIN, STOP_TRYING_TO_BUY]
    report_config('strat_random', config_variables, report_config=True)
    
    # begin trading
    while TRADE_CYCLES_R > 0:

        # generate a random number, select a stock to trade, and report
        random_number = randrange(len(stocks_to_trade))
        symbol_to_trade = [random_symbol[1] for random_symbol in enumerate(stocks_to_trade) if random_number == random_symbol[0]]
        progress.w('WE_WILL_TRADE_(' + str(symbol_to_trade[0]) + ')')

        # place buy order, get details, and report
        order_response = order_place_equity_market(tda_client, OrderType.BUY, symbol_to_trade[0], SHARE_QUANTITY)
        order_json = order_get_details(tda_client, order_response, wait_for_fill=STOP_TRYING_TO_BUY, order_report=True)
        data_syndicate(order_json, report_data=True)

        # sleep between buy and sell
        progress.w('SLEEPING_(hold_position_(' + str(HOLD_STOCK_THIS_LONG) + '_seconds))')
        sleep(HOLD_STOCK_THIS_LONG)

        # place sell order, get details, and report
        order_response = order_place_equity_market(tda_client, OrderType.SELL, symbol_to_trade[0], SHARE_QUANTITY)
        order_json = order_get_details(tda_client, order_response, wait_for_fill=True, order_report=True)
        data_syndicate(order_json, report_data=True, report_lists=True, report_profit=True)

        # sleep before we buy another stock
        progress.w('SLEEPING_(ending_cycle(' + str(TRADE_CYCLE_DEFAULT_R-TRADE_CYCLES_R+1) + ' of ' + str(TRADE_CYCLE_DEFAULT_R) + '))')
        sleep(WAIT_BEFORE_BUYING_AGAIN)

        # decrease TRADE_CYCLES
        TRADE_CYCLES_R = TRADE_CYCLES_R - 1