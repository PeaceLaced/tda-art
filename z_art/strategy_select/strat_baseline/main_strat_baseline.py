"""
- (main_strat_baseline.py)

"""

import sys
from time import sleep
from decimal import Decimal, setcontext, BasicContext
from z_art.progress_report.config_progress_report import Progress as progress

# slowly converting everyting to the new API
from z_art.strategy_select.api_strat_select import OrderType
from z_art.strategy_select.api_strat_select import report_config
from z_art.strategy_select.api_strat_select import data_syndicate
from z_art.strategy_select.api_strat_select import order_get_details
from z_art.strategy_select.api_strat_select import order_place_equity_market

# set decimal context, precision = 9, rounding = round half even
setcontext(BasicContext)

def run_strat_baseline(tda_client, stocks_to_trade):
    '''Trade the BASELINE strat based on config_strat_baseline.py

    :param tda_client: a client object created by tda-api for connecting to TD Ameritrade
    :param stocks_to_trade: list of stocks we want to trade
    :meth order_place_and_parse: place an order and return a json of the details
    :meth report_order_complete: sends a report of the completed order to the TRACE log

    :meth parse_order: returns a json of the order after getting the order id

    '''
    # load variables from config and report
    from z_art.strategy_select.strat_baseline.config_strat_baseline import TRIPPLE_WIN_SHARES, HARDCODED_TEST_SHARES
    from z_art.strategy_select.strat_baseline.config_strat_baseline import HOLD_STOCK_THIS_LONG, TRIPPLE_WIN_MOD
    from z_art.strategy_select.strat_baseline.config_strat_baseline import MINUTES_TO_RUN, STOP_TRYING_TO_BUY
    config_variables = [TRIPPLE_WIN_SHARES, HARDCODED_TEST_SHARES, HOLD_STOCK_THIS_LONG, TRIPPLE_WIN_MOD, MINUTES_TO_RUN, STOP_TRYING_TO_BUY]
    report_config('config_strat_baseline', config_variables, report_config=True)

    # setup some lists and variables to use throughout the strategy
    losers_removed = []
    TRADE_CYCLE_COUNTER = 0
    TRADE_CYCLE_QUIT = 10
    TRADE_CYCLE_SWITCH = 0
    sleep_counter = len(stocks_to_trade)
    sleep_counter_d = len(stocks_to_trade)

    # begin trading and continue running until we meet quit (defined in tripple-win logic)
    while TRADE_CYCLE_QUIT > 0:
        
        # pre tripple win logic, gets us to our tripple win trades
        if TRADE_CYCLE_COUNTER in [0, 1, 2]:

            # loop through list, buy each symbol, wait for fill canceling based on config, report results
            for symbol_to_trade in stocks_to_trade:
                order_response = order_place_equity_market(tda_client, OrderType.BUY, symbol_to_trade, HARDCODED_TEST_SHARES)
                order_json = order_get_details(tda_client, order_response, wait_for_fill=STOP_TRYING_TO_BUY, order_report=True)
                data_syndicate(order_json, report_data=True)

            # report and sleep for HOLD_STOCK_THIS_LONG
            progress.s('SLEEPING_(hold_position_(' + str(HOLD_STOCK_THIS_LONG) + '_seconds))')
            sleep(HOLD_STOCK_THIS_LONG)

            # loop through list, sell each symbol, wait for fill indefinetly, report results
            for symbol_to_trade in stocks_to_trade:
                    order_response = order_place_equity_market(tda_client, OrderType.SELL, symbol_to_trade, HARDCODED_TEST_SHARES)
                    order_json = order_get_details(tda_client, order_response, wait_for_fill=True, order_report=True)
                    profit_list = data_syndicate(order_json, report_data=True, report_lists=True, report_profit=True, return_profit=True)

            for profit_item in profit_list:
                if Decimal(profit_item[1]) <= 0:
                    losers_removed.append((profit_item[0], str(profit_item[1])))
                    stocks_to_trade.remove(profit_item[0])
            progress.crit(losers_removed)
            progress.crit(str(len(stocks_to_trade)) + ' remaining to trade.')

            # exit if we find that our MAIN list is empty
            if len(stocks_to_trade) == 0:
                progress.w('EXITING_(no_stocks_remain_(no_tripple_wins))')
                sys.exit()

            # situate sleep_counter, report sleeping, sleep
            sleep_counter = sleep_counter + len(stocks_to_trade)
            progress.w('SLEEPING_(ending_cycle(' + str(TRADE_CYCLE_COUNTER + 1) + ' of 3)(PRE-TRIPPLE-WIN)')
            sleep(len(stocks_to_trade)*60)

        # tripple win logic, only trade the stocks that won three times in a row
        else:

            # loop through list, buy each symbol, wait for fill canceling based on config, report results
            for symbol_to_trade in stocks_to_trade:
                order_response = order_place_equity_market(tda_client, OrderType.BUY, symbol_to_trade, TRIPPLE_WIN_SHARES)
                order_json = order_get_details(tda_client, order_response, wait_for_fill=STOP_TRYING_TO_BUY, order_report=True)
                data_syndicate(order_json, report_data=True)

            # report and sleep for HOLD_STOCK_THIS_LONG
            progress.s('SLEEPING_(hold_position_(' + str(HOLD_STOCK_THIS_LONG) + '_seconds))')
            sleep(HOLD_STOCK_THIS_LONG)

            # loop through list, sell each symbol, wait for fill indefinetly, report results
            for symbol_to_trade in stocks_to_trade:
                    order_response = order_place_equity_market(tda_client, OrderType.SELL, symbol_to_trade, TRIPPLE_WIN_SHARES)
                    order_json = order_get_details(tda_client, order_response, wait_for_fill=True, order_report=True)
                    data_syndicate(order_json, report_data=True, report_lists=True, report_profit=True)

            # TRADE_CYCLE_QUIT is how many times to cycle the program
            if TRADE_CYCLE_SWITCH == 0:
                from math import floor
                # (wait between trades), (wait between buy/sell), (wait for fills on buy/sell)
                total_minus_pre_tripple_win = (((MINUTES_TO_RUN - (sleep_counter - sleep_counter_d)) * 60) - sleep_counter) - (HOLD_STOCK_THIS_LONG * 3)
                post_tripple_win = (((len(stocks_to_trade)*60) + HOLD_STOCK_THIS_LONG) + (len(stocks_to_trade) * 2))
                TRADE_CYCLE_QUIT = int(floor(total_minus_pre_tripple_win / post_tripple_win))
                TRADE_CYCLE_SWITCH = 1
            TRADE_CYCLE_REPORT = TRADE_CYCLE_COUNTER + TRADE_CYCLE_QUIT

            # sleep before we buy another stock
            progress.w('SLEEPING_(ending_cycle(' + str(TRADE_CYCLE_COUNTER + 1) + ' of ' + str(TRADE_CYCLE_REPORT) +')(TRIPPLE-WIN)')

            # were going to sleep for 60 seconds times the amt of stocks were trading
            TRIPPLE_WIN_SLEEP = TRIPPLE_WIN_MOD * len(stocks_to_trade)

            # sleep based on number of stocks and our modifier (MOD) (default 60 seconds)
            sleep(TRIPPLE_WIN_SLEEP)

        # zero out and clear variables and lists for the next round
        profit_list.clear()
        losers_removed.clear()

        # incriment the trade cycle/trade cycle quit
        TRADE_CYCLE_COUNTER += 1
        TRADE_CYCLE_QUIT -= 1