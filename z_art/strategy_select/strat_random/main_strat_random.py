"""
- (main_strat_random.py)

"""

from time import sleep
from datetime import date
from random import randrange
from tda.client import synchronous
from decimal import Decimal, setcontext, BasicContext

# slowly converting everyting to the new API
from z_art.progress_report.api_progress_report import report_config
from z_art.progress_report.api_progress_report import Progress as progress

from z_art.strategy_select.api_strat_select import OrderType
from z_art.strategy_select.api_strat_select import data_syndicate
from z_art.strategy_select.api_strat_select import order_get_details
from z_art.strategy_select.api_strat_select import order_place_equity_market

# set decimal context, precision = 9, rounding = round half even
setcontext(BasicContext)

class RandomStratTypeException(TypeError):
    '''Raised when there is a type error in :meth:`run_random_strat`.'''
    
class RandomStratValueException(ValueError):
    '''Raised when there is a value error in :meth:`run_random_strat`.'''
    
def run_strat_random(tda_client, stocks_to_trade):
    '''
    Randomly trade stocks by defining constants below.
    - The RANDOM strat takes a list and randomly 
      selects one stock,buys, holds, sells, repeats. 
      Hold is also random, as well as wait time 
      between buying again.
     CAUTION: this strat never wins
    
    :param tda_client: The client object created by tda-api.

    '''
    
    if not isinstance(tda_client, synchronous.Client):
        raise RandomStratTypeException('tda client object is required')
        
    if not isinstance(stocks_to_trade, list):
        raise RandomStratTypeException('stocks_to_trade must be a list')

    TRADE_CYCLE_DEFAULT_R = 300
    TRADE_CYCLES_R = 300
    SHARE_QUANTITY = 1
    
    HOLD_POSITION = 50
    HOLD_TOLERANCE = 10
    
    WAIT_TO_BUY = 10
    WAIT_TOLERANCE = 5
    
    STOP_TRYING_TO_BUY = 10
    
    accumulated_profit = 0
    
    config_variables = [TRADE_CYCLE_DEFAULT_R, TRADE_CYCLES_R, SHARE_QUANTITY, HOLD_POSITION, WAIT_TO_BUY, STOP_TRYING_TO_BUY]
    report_config('strat_random', config_variables, report_config=True)
    
    generated_date = date.today().strftime('%d-%b-%Y')
    file_name = 'z_art/data_visual/data_dump/PROFIT_' + str(generated_date) + '.log'
    f = open(file_name, 'w+')
    f.write(str(0.00))
    f.close()
    
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
        
        # rand tolerance +/-10 seconds from hold
        hold_max = HOLD_POSITION + HOLD_TOLERANCE
        hold_min = HOLD_POSITION - HOLD_TOLERANCE
        new_hold = randrange(hold_min, hold_max)
        
        # sleep between buy and sell
        progress.w('SLEEPING_(hold_position_(' + str(new_hold) + '_seconds))')
        sleep(new_hold)

        # place sell order, get details, and report
        order_response = order_place_equity_market(tda_client, OrderType.SELL, symbol_to_trade[0], SHARE_QUANTITY)
        order_json = order_get_details(tda_client, order_response, wait_for_fill=True, order_report=True)
        profit_data = data_syndicate(order_json, report_data=True, report_lists=True, report_profit=True, return_profit=True)
        
        
        # write accumulation to 'z_art/data_visual/data_dump/PROFIT_dd-mmm-yyyy.log'
        for profit_tuple in profit_data:
            accumulated_profit = Decimal(accumulated_profit) + Decimal(profit_tuple[1])
            f = open(file_name, 'w')
            f.write(str(accumulated_profit))
            f.close()
            
        
        # rand tolerance +/-5 seconds from hold
        buy_again_max = WAIT_TO_BUY + WAIT_TOLERANCE
        buy_again_min = WAIT_TO_BUY - WAIT_TOLERANCE
        new_buy_again = randrange(buy_again_min, buy_again_max)
        
        # sleep before we buy another stock
        progress.w('SLEEPING_(' + str(new_buy_again) + 'seconds)_(cycle(' + str(TRADE_CYCLE_DEFAULT_R-TRADE_CYCLES_R+1) + ' of ' + str(TRADE_CYCLE_DEFAULT_R) + '))')
        sleep(new_buy_again)

        # decrease TRADE_CYCLES
        TRADE_CYCLES_R = TRADE_CYCLES_R - 1
        
        # clear profit data just in case
        profit_data.clear()