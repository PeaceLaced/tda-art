#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 03:42:45 2021

- DO NOT RUN THIS FILE DIRECTLY
    - Instead, USE: (run_automatic_random_trader.py)
    
- script to trade random high volume stocks
- for educational purposes only
- not financial advice

- REQUIREMENTS:
    - tda-api
    - loguru
    - tqdm

@author: brandon (PeaceLaced)
"""

#def cli_main():
async def cli_main():

##############################################################################
######################    CATCH ALL (TOP)    #################################
##############################################################################

    try:
        
##############################################################################
######################    IMPORTS    #########################################
##############################################################################
        import time
        import pytz
        import random
        import requests
        
        from os import system
        from sys import stderr
        from time import sleep
        from datetime import datetime as dt
        
        from loguru import logger
        from tqdm import tqdm, trange
        
        from tda.utils import Utils
        from tda.auth import client_from_token_file
        from tda.orders.common import Session, Duration
        from .config import TOKEN_PATH, API_KEY_TDA, ACCOUNT_ID
        from tda.orders.equities import equity_buy_market, equity_sell_market
        

##############################################################################
######################    LOGGING    #########################################
##############################################################################
# SOURCE: https://github.com/Delgan/loguru 
# info, success, warning and crit all log to stderr
# info, success, warning logs to file MAIN_art_{date}.log
# crit logs to file CRIT_art_{date}.log
##############################################################################
##############################################################################

        ########################################
        ##########  LOGGING FILTER  ############
        ########################################
    
        class MyFilter:
        
            def __init__(self, level):
                self.level = level
        
            def __call__(self, record):
                levelno = logger.level(self.level).no
                return record['level'].no >= levelno
        
        # create instance of myfilter
        my_filter = MyFilter('')
    
        ########################################
        ##########  LOGGING FORMAT  ############
        ########################################
    
        # used to write logs to stderr and file
        def write_log(level, message):
            
            # clear the log every call
            logger.remove()
            
            # format log string
            format_stderr_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '
            format_file_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '
            
            # make sure level is passed correctly
            if level in ['INFO', 'SUCCESS', 'WARNING', 'CRITICAL']:
                    
                if level == 'INFO':
                    my_filter.level = level
                    logger.add('MAIN_art_{time:DD-MMM-YYYY}.log', format=format_file_log, filter=my_filter, level=0)
                    logger.add(stderr, format=format_stderr_log, filter=my_filter, level=0)
                    logger.info(message)
                    
                elif level == 'SUCCESS':
                    my_filter.level = level
                    logger.add('MAIN_art_{time:DD-MMM-YYYY}.log', format=format_file_log, filter=my_filter, level=0)
                    logger.add(stderr, format=format_stderr_log, filter=my_filter, level=0)
                    logger.success(message)
        
                elif level == 'WARNING':
                    my_filter.level = level
                    logger.add('MAIN_art_{time:DD-MMM-YYYY}.log', format=format_file_log, filter=my_filter, level=0)
                    logger.add(stderr, format=format_stderr_log, filter=my_filter, level=0)
                    logger.warning(message)
                    
                elif level == 'CRITICAL':
                    my_filter.level = level
                    logger.add('CRIT_art_{time:DD-MMM-YYYY}.log', format=format_file_log, filter=my_filter, level=0)
                    logger.add(stderr, format=format_stderr_log, filter=my_filter, level=0)
                    logger.critical(message)
        
            # warn when we use write_log incorrectly 
            else:
                my_filter.level = 'WARNING'
                logger.add(stderr, format=format_stderr_log, filter=my_filter, level=0)
                logger.warning('\n the level (' + level + ') ' + 'must be INFO, SUCCESS, WARNING, CRITICAL')
            
        ########################################
        ##########  LOGGING PROGRESS  ##########
        ########################################
    
        # INFO progress
        def progress_i(msg):
            write_log('INFO', msg)
        
        # SUCCESS progress
        def progress_s(msg):
            write_log('SUCCESS', msg)
            
        # WARNING progress
        def progress_w(msg):
            write_log('WARNING', msg)
        
        # CRITICAL progress
        def progress_c(msg):
            write_log('CRITICAL', msg)
        
##############################################################################
######################    CUSTOM FUNCTIONS    ################################
##############################################################################

        #########################################
        ##########  CLEAR FUNCTION    ###########
        ######################################### 
        # clear the CLI        
        def clear():
            _ = system('clear')
        clear()
        ########################################
        ##########  MISC PROGRESS  #############
        ########################################
        
        # SLOW progress
        def progress_slow(msg):
            for c in msg +'\n':
                stderr.write(c)
                stderr.flush()
                sleep(1./20)
                
        # PRINT progress
        def progress_print(msg):
            tqdm.write(msg)
            
        # INPUT progress
        def progress_input(msg):
            input(msg)
            
        # TQDM progress
        def progress_tqdm(msg):
            for c in trange(100, desc=msg):
                pass
        
##############################################################################
######################    IDENTIFY SCRIPT    #################################
##############################################################################

        progress_w('IDENTIFY_SCRIPT_(run_automatic_random_trader.py)')

##############################################################################
######################    TIMER INIT    ######################################
##############################################################################

        # Time Counter for simple Run Length used during Boot Sequence and Shutdown.
        s = time.perf_counter()
        progress_s('INITIALIZE_TIMER')
        
##############################################################################
######################    END CATCH ALL TOP    ###############################
##############################################################################

    except Exception as err:
        progress_c(f'Unexpected {err=}, {type(err)=} (catch_all_top)')
        
##############################################################################
######################    TDA CONNECT    #####################################
##############################################################################
# TDA-API DOCS:     https://tda-api.readthedocs.io/en/latest/
# TDA-API SOURCE:   https://github.com/alexgolec/tda-api
# TDA-API DISCORD:  https://discord.gg/M3vjtHj
##############################################################################
##############################################################################

    # TDA-API Client.
    progress_i('TDA_TOKEN_(search)')
    try:
        tda_client = client_from_token_file(TOKEN_PATH, API_KEY_TDA)

    # create TDA token and clients if token file is not found
    except FileNotFoundError:
        
        progress_w('TDA_TOKEN_(not_found)')
        from selenium import webdriver
        from tda.auth import client_from_login_flow
        from .config import REDIRECT_URI
        
        progress_i('TDA_TOKEN_(create)')
        with webdriver.Firefox() as DRIVER:
            tda_client = client_from_login_flow(
                DRIVER, API_KEY_TDA, REDIRECT_URI, TOKEN_PATH)
    
    except Exception as err:
        progress_c(f'Unexpected {err=}, {type(err)=} (catch_all_tda-api)')
        
    progress_s('TDA_TOKEN_(found)')
    
##############################################################################
######################    KBInterrupt and CATCH ALL (bottom)    ##############
##############################################################################
    try:
##############################################################################
######################    BOOT SECTION    ####################################
##############################################################################
# UNDERSTAND THESE VARIABLES BEFORE YOU CONTINUE
#
#   HOLD_STOCK_THIS_LONG + WAIT_BEFORE_BUYING_AGAIN
#       = how often this script will buy a stock
#           EXAMPLE: 50 + 10 = every 60 seconds
#
#   Multiply that number by TRADE_CYCLES
#       = and you get how long the script will run
#           REMEMBER: Fill delay will increase this time
#
#   Lastly, BUY orders will cancel if STOP_TRYING_TO_BUY is met,
#       However, there is no cancel when SELL orders do not fill.
#           CAUTION: Some sell orders may remain open, keep a close eye.
#
#   Good luck and happy trading,
#       ~ Peace
##############################################################################
##############################################################################

        ###########################################
        ########  SCRIPT CONTROL VARIABLES  #######
        ###########################################
        
        # how many high (volume/volatility) stocks do we want to select from
        # TODO: use thi sin place of VOLATILITY_THRESHOLD <>
        HIGH_VOL_STOCKS = 25
        
        # volatility threshold, VOLATILITY_THRESHOLD > abs(0-netchange) where netchange is (day before yesterday - yesterday)
        VOLATILITY_THRESHOLD = 0.1
        
        # high, low, both. High is above positive threshold, low is below negative threshold, both is both
        # TODO: both NOT working yet<>
        VOLATILITY_BALANCE = 'HIGH'
        
        # how many shares will we buy each round
        SHARE_QUANTITY = 1
        
        # only select stocks between these two price points
        STOCK_PRICE_LOW = 2.00
        STOCK_PRICE_HIGH = 5.00
        
        # how long should we hold the stock, in seconds
        HOLD_STOCK_THIS_LONG = 50
        
        # after selling, how long before we buy again, in seconds
        WAIT_BEFORE_BUYING_AGAIN = 10
        
        # stop trying to buy a stock if it fails to fill, in seconds
        STOP_TRYING_TO_BUY = 10
        
        # how many times should we attempt a buy/sell today
        TRADE_CYCLES = 200
        
        # this limit stops the script when it is reached, for cash accounts only
        CASH_AVAILABLE_FOR_TRADE_LIMIT = 5000
        
        # if you do NOT want certain stocks to be traded, add them here
        # TODO: THIS IS NOT IMPLEMENTED YET <>
        AVOID_THESE_STOCKS = []
        
        # report variables the log
        def report_control_variables():
            progress_w('(' + str(HIGH_VOL_STOCKS) + ')_HIGH_VOL_STOCKS')
            progress_w('(' + str(VOLATILITY_THRESHOLD) + ')_VOLATILITY_THRESHOLD')
            progress_w('(' + str(VOLATILITY_BALANCE) + ')_VOLATILITY_THRESHOLD_BALANCE')
            progress_w('(' + str(SHARE_QUANTITY) + ')_SHARE_QUANTITY')
            progress_w('(' + str(STOCK_PRICE_LOW) + ')_STOCK_PRICE_LOW')
            progress_w('(' + str(STOCK_PRICE_HIGH) + ')_STOCK_PRICE_HIGH')
            progress_w('(' + str(HOLD_STOCK_THIS_LONG) + ')_HOLD_STOCK_THIS_LONG')
            progress_w('(' + str(WAIT_BEFORE_BUYING_AGAIN) + ')_WAIT_BEFORE_BUYING_AGAIN')
            progress_w('(' + str(STOP_TRYING_TO_BUY) + ')_STOP_TRYING_TO_BUY')
            progress_w('(' + str(TRADE_CYCLES) + ')_TRADE_CYCLES')
            progress_w('(' + str(CASH_AVAILABLE_FOR_TRADE_LIMIT) + ')_CASH_AVAILABLE_FOR_TRADE_LIMIT')

        report_control_variables()
        progress_s('REPORT_VARIABLES')
        ###########################################
        ########  REPORT BOOT TIME  ###############
        ########################################### 
        
        # boot timer for reference
        boot_elapsed = time.perf_counter() - s
        progress_w(f"boot_elapsed in {boot_elapsed:0.2f} seconds.")
        
        ###########################################
        ########  BOOT SUCCESSFUL  ################
        ########################################### 
        progress_slow('Boot Successful. Double check your variables. Press ENTER to continue:')
        progress_input('')
        
##############################################################################
######################    RUN APPLICATION    #################################
##############################################################################
     
        ###########################################
        ########  GET TDA ACCOUNT INFO  ###########
        ###########################################

        # get account information from TDA and convert to json
        account_info = tda_client.get_account(int(ACCOUNT_ID)).json()
        progress_s('GET_TDA_ACCOUNT_INFORMATION')
        
        # get account type from the account information
        tda_account_type = account_info['securitiesAccount']['type']
        progress_i('WORKING_WITH_ACOUNT_TYPE_(' + str(tda_account_type) + ')')
        
        # extract all cashAvailableForTrading values from the data, return the lowest value
        def get_cash_available_for_trade():
            # get the three cashAvailableForTrading entries
            tda_initial_trade_cash_available = account_info['securitiesAccount']['initialBalances']['cashAvailableForTrading']
            tda_current_trade_cash_available = account_info['securitiesAccount']['currentBalances']['cashAvailableForTrading']
            tda_projected_trade_cash_available = account_info['securitiesAccount']['projectedBalances']['cashAvailableForTrading']
            
            # find the lowest value of the three to make sure we stay within our limit
            estimated_cash_available_for_trade = min(tda_initial_trade_cash_available,
                                                     tda_current_trade_cash_available,
                                                     tda_projected_trade_cash_available)
            
            return estimated_cash_available_for_trade

        ###########################################
        ########  GET NASDAQ SCREENER  ############
        ###########################################
        def get_nasdaq_screener():
            
            # Get the NEW nasdaq screener from API and convert it to JSON
            nasdaq_screener_nowpull = requests.get('https://api.nasdaq.com/api/screener/stocks', 
                                                   params={'tableonly' : 'true', 'limit' : 15000,'exchange' : 'all'}, 
                                                   headers={"User-Agent": "Mozilla/5.0 (x11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"}
                                                   ).json()
            progress_s('GET_NASDAQ_SCREENER')
            
            # Use asof date to create aware datetime for NEW nasdaq screener
            asof_trimmed = nasdaq_screener_nowpull['data']['asof'].replace('Last price as of','').replace(',','').split()
            new_asof = dt.strptime(asof_trimmed[1] + ' ' + asof_trimmed[0] + ' ' + asof_trimmed[2], "%d %b %Y")
            ns_nowpull_aware_datetime = pytz.timezone('US/Eastern').localize(dt(new_asof.year, new_asof.month, new_asof.day, 20))
            progress_s('CREATE_AWARE_DT')
            
            # return both the data and the aware datetime (useful if writing to a database)
            return nasdaq_screener_nowpull, ns_nowpull_aware_datetime
        
        # grab the nasdaq screener, grab the data to pass into our top vol/price limit function
        ns = get_nasdaq_screener()
        nasdaq_screener_data = ns[0]

        ###########################################
        ########  GET VOLATILE STOCKS  ############
        ###########################################

        # nasdaq_screener_data, HIGH_VOL_STOCKS, STOCK_PRICE_LOW, STOCK_PRICE_HIGH, 
        #                       AVOID_THESE_STOCKS, VOLATILITY_THRESHOLD, VOLATILITY_BALANCE
        def get_top_volume_stocks_price_limited(nsd, hvs, spl, sph, ats, vt, vb):
            
            # create an empty list to fill as we filter the data
            top_vol_stocks_price_limited = []
            
            # tuple the useful data (symbol, lastsale, netchange, marketCap)
            for symbol_data in nsd['data']['table']['rows']:
                symbol_data_tuple = (symbol_data['symbol'], 
                                     symbol_data['lastsale'].replace('$',''), 
                                     symbol_data['netchange'],
                                     symbol_data['marketCap'])
                
                # remove symbols that contain slash, carrot, or space
                if symbol_data_tuple[0].find(
                        '^') == -1 and symbol_data_tuple[0].find(
                            '/') == -1 and symbol_data_tuple[0].find(
                                ' ') == -1: 
                    
                    # get rid of netchange that contain UNCH
                    if symbol_data_tuple[2].find('UNCH') == -1:
                        
                        # only grab stocks between our high and low
                        if float(symbol_data_tuple[1]) > spl and float(symbol_data_tuple[1]) < sph:
                            
                            # get rid of marketCap with NA
                            if symbol_data_tuple[3] != 'NA':
                            
                                # meet our volatility threshold/balance
                                volatility_of_point = 0.0 - float(symbol_data_tuple[2])
                                
                                if vb == 'HIGH' and volatility_of_point < 0.0:
                                    if abs(volatility_of_point) > vt:
                                        # put each tuple into our list
                                        top_vol_stocks_price_limited.append(symbol_data_tuple)
                                        
                                elif vb == 'LOW' and volatility_of_point > 0.0:
                                    if float(volatility_of_point) > vt:
                                        # put each tuple into our list
                                        top_vol_stocks_price_limited.append(symbol_data_tuple)
                                        
                                elif vb == 'BOTH':
                                    pass

            # return our list of symbols, which we will trade on
            return top_vol_stocks_price_limited

        # FUTURE USE TO GET TOP VOLATILITY INSTEAD OF USING THRESHOLD
        '''
        def ret_2nd_ele(tuple_1):
            return tuple_1[1]
        
        # remove lowest volume symbols until we have QUANTITY specified
        pbar = tqdm(total=len(vol_data)-TOP_VOLUME_PREVIOUS_DAY)
        while len(vol_data) > TOP_VOLUME_PREVIOUS_DAY:
            pbar.set_description('REMOVING_LOW_VOLUME')
            vol_data.remove(min(vol_data, key=ret_2nd_ele))
            pbar.update(1)
        pbar.close()
        progress_s('REMOVED_LOWEST_VOLUME_SYMBOLS')
        '''
        
        # run the filter function and get our stock tuples
        stock_tuples = get_top_volume_stocks_price_limited(nasdaq_screener_data, 
                                                              HIGH_VOL_STOCKS, 
                                                              STOCK_PRICE_LOW, 
                                                              STOCK_PRICE_HIGH,
                                                              AVOID_THESE_STOCKS,
                                                              VOLATILITY_THRESHOLD,
                                                              VOLATILITY_BALANCE)
        
        # pull the symbol from the tuple and report
        stocks_to_trade = []
        for stock in stock_tuples:
            stocks_to_trade.append(stock[0])
        progress_slow('COUNT: ' + str(len(stocks_to_trade)) + ' (stock pool to randomly select from)')
        progress_input('Press ENTER to continue.')
        
        ###########################################
        ########  MAIN CASH ACCOUNT LOOP  #########
        ###########################################   
        # if our account type is cash, everything we do will be based on cashAvailableForTrading
        if tda_account_type == 'CASH':
            
            # get cash available for trade 
            cash_available_for_trade = get_cash_available_for_trade()
            
            # only trade if we are above our limit (cashAvailableForTrading decreases as we make trades)
            while cash_available_for_trade > CASH_AVAILABLE_FOR_TRADE_LIMIT:
                
                # stop trading when we reach TRADE_CYCLES limit
                while TRADE_CYCLES > 0:
                    
                    ###########################################
                    ########  RANDOMLY SELECT A SYMBOL  #######
                    ###########################################
                    
                    # generate a random number between 0 and our HIGH_VOL_STOCKS
                    random_number = random.randrange(len(stocks_to_trade))
                    progress_s('GENERATE_RANDOM_NUMBER')
                    
                    # enumerate our list and randomly select a symbol
                    symbol_to_trade = [random_symbol[1] for random_symbol in enumerate(stocks_to_trade) if random_number == random_symbol[0]]
                    progress_s('SELECT_RANDOM_SYMBOL')
                    progress_c('WE_WILL_TRADE_(' + str(symbol_to_trade[0]) + ')')
                    
                    ###########################################
                    ########  PLACE BUY ORDER  ################
                    ###########################################
                    
                    # buy the random stock
                    progress_i('PLACING_AN_ORDER_(buy_random_(' + symbol_to_trade[0] + '))')
                    try:
                        
                        # build and place buy order
                        buy_order_response = tda_client.place_order(int(ACCOUNT_ID), equity_buy_market(symbol_to_trade[0], SHARE_QUANTITY))
                        
                        # extract the order ID from the placed order
                        buy_order_id = Utils(tda_client, 
                                             int(ACCOUNT_ID)
                                             ).extract_order_id(buy_order_response)
                        
                        # pull the details of the order
                        get_buy_order = tda_client.get_order(buy_order_id, int(ACCOUNT_ID))
                        
                        # convert the order details to JSON
                        buy_order_json = get_buy_order.json()
                        
                        # crit the DATA
                        progress_c(buy_order_json)
                        
                        # check to make sure the order filled
                        if buy_order_json['filledQuantity'] != 1:
                            while buy_order_json['filledQuantity'] < 1:
                                
                                sleep_counter = 0
                                while sleep_counter < 10:
                                    
                                    # sleep for 1 second
                                    progress_w('WAITING_FOR_FILL_(' + symbol_to_trade[0] + ')')
                                    sleep(1)
                                    
                                    # pull the details of the order
                                    get_buy_order = tda_client.get_order(buy_order_id, int(ACCOUNT_ID))
                                    
                                    # convert the order details to JSON
                                    buy_order_json = get_buy_order.json()
                                    
                                    if buy_order_json['filledQuantity'] == 1:
                                        break
                                    else:
                                        # add to sleep counter
                                        sleep_counter = sleep_counter + 1
                                
                                # cancel the order if we get to this point
                                if sleep_counter == 10:
                                    cancel_buy_order_response = tda_client.cancel_order(buy_order_id, int(ACCOUNT_ID))
                                    cancel_buy_order_json = cancel_buy_order_response.json()                       
                        
                                    # CRIT the data
                                    progress_c(cancel_buy_order_json)
                                    # TODO crit only useful infos <>
                        
                    except Exception as err:
                        progress_c(f'Unexpected {err=}, {type(err)=} (' + symbol_to_trade[0] + ')') 
                    progress_s('PLACING_AN_ORDER_(buy_random_(' + symbol_to_trade[0] + '))')
                    
                    ###########################################
                    ########  SLEEP BEFORE SELL  ##############
                    ###########################################
                    
                    # sleep for however long we want to hold the stock
                    sleep(HOLD_STOCK_THIS_LONG)
                    progress_s('SLEEPING_(' + str(HOLD_STOCK_THIS_LONG) + '_seconds)')
                    
                    ###########################################
                    ########  PLACE SELL ORDER  ###############
                    ###########################################
                    
                    # sell the random stock
                    progress_i('PLACING_AN_ORDER_(sell_random_(' + symbol_to_trade[0] + '))')
                    try:
                        
                        # build and place the sell order
                        sell_order_response = tda_client.place_order(int(ACCOUNT_ID), equity_sell_market(symbol_to_trade[0], SHARE_QUANTITY))
                        #.set_session(Session.SEAMLESS).set_duration(Duration.GOOD_TILL_CANCEL)
                        
                        # extract the order ID from the placed order
                        sell_order_id = Utils(tda_client, 
                                              int(ACCOUNT_ID)
                                              ).extract_order_id(sell_order_response)
                        
                        # pull the details of the order
                        get_sell_order = tda_client.get_order(sell_order_id, int(ACCOUNT_ID))
                        
                        # convert the order details to JSON
                        sell_order_json = get_sell_order.json()
                        
                        if sell_order_json['filledQuantity'] != 1:
                            while sell_order_json['filledQuantity'] < 1:
                                
                                # sleep for 1 second
                                progress_w('WAITING_FOR_FILL_(' + symbol_to_trade[0] + ')')
                                sleep(1)
                                
                                # pull the details of the order
                                get_sell_order = tda_client.get_order(sell_order_id, int(ACCOUNT_ID))
                                
                                # convert the order details to JSON
                                sell_order_json = get_sell_order.json()
                        
                        # fill is successful, report it
                        progress_s('WAITING_FOR_FILL_(' + symbol_to_trade[0] + ')')
                        
                        # CRIT the data
                        progress_c(sell_order_json)
                        # TODO crit only useful infos <>
                    
                    except Exception as err:
                        progress_c(f'Unexpected {err=}, {type(err)=} (' + symbol_to_trade[0] + ')')
                    progress_s('PLACING_AN_ORDER_(' + symbol_to_trade[0] + '))')

                    ###########################################
                    ########  SLEEP BEFORE BUY  ###############
                    ###########################################
                    
                    # sleep before we buy another stock
                    sleep(WAIT_BEFORE_BUYING_AGAIN)
                    progress_s('SLEEPING_(' + str(WAIT_BEFORE_BUYING_AGAIN) + '_seconds)')
                    
                    # decrease TRADE_CYCLES
                    TRADE_CYCLES = TRADE_CYCLES - 1
                
                    if TRADE_CYCLES > 0:
                        
                        # continue to check if we have enough cash available to trade    
                        cash_available_for_trade = get_cash_available_for_trade()
                        progress_i(cash_available_for_trade)

        ###########################################
        ########  OTHER(margin?) ACCOUNT LOOP  ####
        ########################################### 
        # what other types of account are there, becides cash? (margin?)
        else:
            
            progress_i('TODO: trade logic for MARGIN/Other')

##############################################################################
######################    APPLICATION SHUTDOWN and EXIT TIMER    #############
##############################################################################
        
        # normal shutdown
        progress_s('APPLICATION_SHUTDOWN_(normal)')
    
    except KeyboardInterrupt:
        
        # kbi shutdown
        progress_s('APPLICATION_SHUTDOWN_(KBInterrupt)')
        
    except Exception as err:
        
        progress_c(f'Unexpected {err=}, {type(err)=} (catch_all_bottom)')
        
    # Report Application Run Time
    whole_elapsed = time.perf_counter() - s
    progress_w(f"whole_elapsed in {whole_elapsed:0.2f} seconds.")

##############################################################################
######################    RUN MAIN AS FILE (NOT RECOMMENDED)   ###############
##############################################################################
if __name__ == '__main__':
    print('running cli_main() from inside __name__ == __main__')
    cli_main()