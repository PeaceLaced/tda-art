#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 03:42:45 2021

- DO NOT RUN THIS FILE DIRECTLY
    - Instead, USE: (run_automatic_random_trader.py)
    
- script to trade high volatility stocks, randomly
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
######################    CATCH ALL (boot)    #################################
##############################################################################

    try:
        
##############################################################################
######################    IMPORTS    #########################################
##############################################################################
    
        import sys
        import time
        import pytz
        import random
        import requests
        
        from os import system
        from sys import stderr
        from time import sleep
        from datetime import datetime as dt
        from decimal import setcontext, BasicContext, Decimal
        
        from loguru import logger
        from tqdm import tqdm, trange
        
        from tda.utils import Utils
        from tda.auth import client_from_token_file
        from tda.orders.common import Session, Duration
        from .config import TOKEN_PATH, API_KEY_TDA, ACCOUNT_ID
        from tda.orders.equities import equity_buy_market, equity_sell_market
        

##############################################################################
#######                 LOGGING with LOGURU                           ########
#######                ---------------------                          ########
####### LOGURU DOCS:      https://loguru.readthedocs.io/en/stable/    ########
####### LOGURU SOURCE:    https://github.com/Delgan/loguru            ########
#######                                                               ########
####### NOTE: To reflect actual line numbers in log, see USE IN-LINE  ########
#######       Also, see PROGRESS LOGGING methods for how to use.      ########
#######                                                               ########
####### USE IN-LINE:                                                  ########
#######     - logger.remove()                                         ########
#######     - logger.add('xxx.log') ['TRACE', 'DEBUG', 'CRITICAL']    ########
#######     - logger.add(stderr)    ['TRACE', 'DEBUG', 'CRITICAL']    ########
#######     - logger.trace('message')                                 ########
#######     - logger.debug('message')                                 ########
#######     - logger.critical('message')                              ########
#######                                                               ########
##############################################################################
######################    Pre-boot area for testing   ########################
##############################################################################

##############################################################################
##############################################################################
##############################################################################
        
        # PROGRESS LOGGING
        class Progress:
            
            # set up log format for stderr and file
            def __init__(self):
                self.format_stderr_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '
                self.format_file_log = '<green>{time:YYYY-MM-DD HH:mm:ss}</> | <lvl>{level:<8}</> | <lvl>{message}</> '
                
            ####################################
            ####   MAIN PROGRESS METHODS    ####
            ####  -----------------------   ####
            ####  These log to:             ####
            ####    - stderr                ####
            ####    - MAIN_art_{d}.log      ####
            ####                            ####
            ####  Options:                  ####
            ####    - i = INFO              ####
            ####    - s = SUCCESS           ####
            ####    - w = WARNING           ####
            ####    - e = ERROR             ####
            ####                            ####
            ####################################
            
            def i(self, message):
                logger.remove()
                logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format=self.format_file_log, level='INFO')
                logger.add(stderr, format=self.format_stderr_log, level='INFO')
                logger.info(message)
                
            def s(self, message):
                logger.remove()
                logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='SUCCESS')
                logger.add(stderr, format=self.format_stderr_log, level='SUCCESS')
                logger.success(message)
            
            def w(self, message):
                logger.remove()
                logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='WARNING')
                logger.add(stderr, format=self.format_stderr_log, level='WARNING')
                logger.warning(message)
            
            def e(self, message):
                logger.remove()
                logger.add('LOGS/MAIN_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='ERROR')
                logger.add(stderr, format=self.format_stderr_log, level='ERROR')
                logger.error(message)
            
            # use for logging symbol, buy, sell price for easy parsing    
            def crit(self, message):
                logger.remove()
                logger.add('LOGS/CRIT_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='CRITICAL')
                logger.add(stderr, format=self.format_stderr_log, level='CRITICAL')
                logger.critical(message)
                
            # use to log buy and sell JSON data, FILE ONLY   
            def debug(self, message):
                logger.remove()
                logger.add('LOGS/DEBUG_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='DEBUG')
                logger.debug(message)
                
            # use to log profit/loss from each buy/sell combo   
            def trace(self, message):
                logger.remove()
                logger.add('LOGS/TRACE_art_{time:DD-MMM-YYYY}.log', format= self.format_file_log, level='TRACE')
                logger.add(stderr, format=self.format_stderr_log, level='TRACE')
                logger.trace(message)
                
            ####################################
            ####   MISC PROGRESS METHODS    ####
            ####  -----------------------   ####
            ####################################
            
            # writes to stderr slowly
            def slowly(self, msg):
                for c in msg +'\n':
                    stderr.write(c)
                    stderr.flush()
                    sleep(1./20)
                    
            # writes to stderr
            def printly(self, msg):
                tqdm.write(msg)
                
            # normal input
            def inputly(self, msg):
                input(msg)
                
            # TQDM progress bar
            def tqdmly(self, msg):
                for c in trange(100, desc=msg):
                    pass

            # clear the CLI        
            def clearly(self):
                _ = system('clear')
                
        # instantiate the progress class for logging
        progress = Progress()
        progress.clearly()

##############################################################################
######################    IDENTIFY SCRIPT    #################################
##############################################################################

        progress.w('IDENTIFY_SCRIPT_(run_automatic_random_trader.py)')

##############################################################################
######################    TIMER INIT    ######################################
##############################################################################

        # Time Counter for simple Run Length used during Boot Sequence and Shutdown.
        s = time.perf_counter()
        progress.s('INITIALIZE_TIMER')
        
##############################################################################
######################    END CATCH ALL TOP    ###############################
##############################################################################

    except Exception as err:
        progress.e(f'Unexpected {err=}, {type(err)=} (catch_all_boot)')
        
##############################################################################
#######     TD Ameritrade connection and processing with TDA-API      ########
#######    ------------------------------------------------------     ########
####### TDA-API DOCS:     https://tda-api.readthedocs.io/en/latest/   ########
####### TDA-API SOURCE:   https://github.com/alexgolec/tda-api        ########
####### TDA-API DISCORD:  https://discord.gg/M3vjtHj                  ########
#######                                                               ########
##############################################################################

    # TDA-API Client.
    progress.i('TDA_TOKEN_(search)')
    try:
        tda_client = client_from_token_file(TOKEN_PATH, API_KEY_TDA)

    # create TDA token and clients if token file is not found
    except FileNotFoundError:
        
        progress.w('TDA_TOKEN_(not_found)')
        from selenium import webdriver
        from tda.auth import client_from_login_flow
        from .config import REDIRECT_URI
        
        progress.i('TDA_TOKEN_(create)')
        with webdriver.Firefox() as DRIVER:
            tda_client = client_from_login_flow(
                DRIVER, API_KEY_TDA, REDIRECT_URI, TOKEN_PATH)
    
    except Exception as err:
        progress.e(f'Unexpected {err=}, {type(err)=} (catch_all_tda-api)')
        
    progress.s('TDA_TOKEN_(found)')
    
##############################################################################
######################    KBInterrupt and CATCH ALL (application)   ##########
##############################################################################
    try:

        ####################################
        ####  TDA ACCOUNT VARIABLES     ####
        #### -------------------------- ####
        ####################################
        
        # how much money do you want to spend today?
        CASH_TO_SPEND = 2000
        
        # keep your TDA account above this cash threshold
        CASH_AVAILABLE_THRESHOLD = 3000
        
        ####################################
        ####  STOCK SELECT VARIABLES    ####
        #### -------------------------- ####
        ####################################
        
        # how many stocks do you want in the pool to randomly pick from
        # TODO: keep this number high until I finish the filter logic <>
        NUMBER_OF_STOCKS_IN_POOL = 200
        
        # consider market cap before volatility?
        # TODO: not implemented yet <>
        CONSIDER_MARKET_CAP = 'YES'
        
        # TOP or BOTTOM, both are high volatility, top is positive, bottom is negative
        VOLATILITY_TAIL = 'TOP'
        
        # VOLATILITY_THRESHOLD > abs(0-netchange) where netchange is (day_before_yesterday - yesterday)
        VOLATILITY_THRESHOLD = 0.1

        # only select stocks between these two price points
        STOCK_PRICE_LOW = 2.00
        STOCK_PRICE_HIGH = 5.00
        
        # manually add stocks to the pick list
        # TODO: not implemented yet <>
        ADD_THESE_STOCKS = []
        
        # filter out these stocks from the pick list
        # TODO: not implemented yet <>
        AVOID_THESE_STOCKS = []
        
        ####################################
        ####  STOCK TRADE VARIABLES     ####
        #### -------------------------- ####
        ####################################        
                
        # these two numbers should stay the same
        # how many times do we want to buy and sell a random stock
        # trade_cycle means, take position this many times
        TRADE_CYCLE_DEFAULT = 300
        TRADE_CYCLES = 300   
        
        # how many shares will we buy each round
        # TODO: propigate SHARE_QUANTITY to buy/sell checks after KILL_OR_FILL is added <>
        SHARE_QUANTITY = 1
        
        # how long should we hold the stock, in seconds
        HOLD_STOCK_THIS_LONG = 50
        
        # after selling, how long before we buy again, in seconds
        WAIT_BEFORE_BUYING_AGAIN = 10
        
        # stop trying to buy a stock if it fails to fill, in seconds
        STOP_TRYING_TO_BUY = 10
        
        # report variables to the log
        def report_control_variables():
            progress.w('(' + str(CASH_TO_SPEND) + ')_CASH_TO_SPEND')
            progress.w('(' + str(CASH_AVAILABLE_THRESHOLD) + ')_CASH_AVAILABLE_THRESHOLD')
            progress.w('(' + str(NUMBER_OF_STOCKS_IN_POOL) + ')_NUMBER_OF_STOCKS_IN_POOL')
            progress.w('(' + str(CONSIDER_MARKET_CAP) + ')_CONSIDER_MARKET_CAP')
            progress.w('(' + str(VOLATILITY_TAIL) + ')_VOLATILITY_TAIL')
            progress.w('(' + str(VOLATILITY_THRESHOLD) + ')_VOLATILITY_THRESHOLD')
            progress.w('(' + str(STOCK_PRICE_LOW) + ')_STOCK_PRICE_LOW')
            progress.w('(' + str(STOCK_PRICE_HIGH) + ')_STOCK_PRICE_HIGH')
            progress.w('(' + str(len(ADD_THESE_STOCKS)) + ')_ADDING_THIS_COUNT')
            progress.w('(' + str(len(AVOID_THESE_STOCKS)) + ')_REMOVING_THIS_COUNT')
            progress.w('(' + str(TRADE_CYCLE_DEFAULT) + ')_TRADE_CYCLE_DEFAULT')
            progress.w('(' + str(TRADE_CYCLES) + ')_TRADE_CYCLES')
            progress.w('(' + str(SHARE_QUANTITY) + ')_SHARE_QUANTITY')
            progress.w('(' + str(HOLD_STOCK_THIS_LONG) + ')_HOLD_STOCK_THIS_LONG')
            progress.w('(' + str(WAIT_BEFORE_BUYING_AGAIN) + ')_WAIT_BEFORE_BUYING_AGAIN')
            progress.w('(' + str(STOP_TRYING_TO_BUY) + ')_STOP_TRYING_TO_BUY')

        report_control_variables()
        progress.s('REPORT_VARIABLES')

        ####################################
        ####      SET DECIMAL CONTEXT   ####
        ####     ---------------------  ####
        ####################################
        
        # basic context is decimal precision = 9 and rounding = round half even
        setcontext(BasicContext)
        
        ####################################
        ####      REPORT BOOT TIME      ####
        ####     ------------------     ####
        ####################################
        
        # boot timer for reference
        boot_elapsed = time.perf_counter() - s
        progress.w(f"boot_elapsed in {boot_elapsed:0.2f} seconds.")
        
        ####################################
        ####      BOOT SUCCESSFUL       ####
        ####     -----------------      ####
        ####################################
        
        progress.slowly('Boot Successful. Double check your variables. Press ENTER to continue:')
        progress.inputly('')
        
##############################################################################
######################    RUN APPLICATION    #################################
##############################################################################
     
        ####################################
        ####  GET TDA ACCT INFORMATION  ####
        #### -------------------------- ####
        ####################################

        # get account information from TDA and convert to json
        account_info = tda_client.get_account(int(ACCOUNT_ID)).json()
        progress.s('GET_TDA_ACCOUNT_INFORMATION')
        
        # get account type from the account information
        tda_account_type = account_info['securitiesAccount']['type']
        progress.i('TDA_ACCOUNT_(TYPE: ' + str(tda_account_type) + ')')
        
        # get cash available for trading
        cash_available_for_trading = account_info['securitiesAccount']['currentBalances']['cashAvailableForTrading']
        progress.w('TDA_ACCOUNT_(CASH: ' + str(cash_available_for_trading) + ')')
        
        # check if we have enough cash in our account
        if cash_available_for_trading - CASH_TO_SPEND > CASH_AVAILABLE_THRESHOLD:
            progress.s('CASH_CHECK_VERIFIED')
        else:
            progress.w('NOT_ENOUGH_CASH')
            progress.slowly("You're trying to spend to much or the threshold is to high. Please Adjust.")
            progress.inputly('Press ENTER to EXIT')
            sys.exit()

        ####################################
        ####    GET NASDAQ SCREENER     ####
        ####   ---------------------    ####
        ####################################
        def get_nasdaq_screener():
            
            # Get the NEW nasdaq screener from API and convert it to JSON
            nasdaq_screener_nowpull = requests.get('https://api.nasdaq.com/api/screener/stocks', 
                                                   params={'tableonly' : 'true', 'limit' : 15000,'exchange' : 'all'}, 
                                                   headers={"User-Agent": "Mozilla/5.0 (x11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"}
                                                   ).json()
            progress.s('GET_NASDAQ_SCREENER')
            
            # Use asof date to create aware datetime for NEW nasdaq screener
            asof_trimmed = nasdaq_screener_nowpull['data']['asof'].replace('Last price as of','').replace(',','').split()
            new_asof = dt.strptime(asof_trimmed[1] + ' ' + asof_trimmed[0] + ' ' + asof_trimmed[2], "%d %b %Y")
            ns_nowpull_aware_datetime = pytz.timezone('US/Eastern').localize(dt(new_asof.year, new_asof.month, new_asof.day, 20))
            progress.s('CREATE_AWARE_DT')
            
            # return both the data and the aware datetime (useful if writing to a database)
            return nasdaq_screener_nowpull, ns_nowpull_aware_datetime
        
        # grab the nasdaq screener, grab the data to pass into our top volatility/price limit function
        ns = get_nasdaq_screener()
        nasdaq_screener_data = ns[0]
        
        ####################################
        ####    GET VOLATILE STOCKS     ####
        ####   ---------------------    ####
        ####################################
        
        # NASDAQ_SCREENER_DATA, NUMBER_OF_STOCKS_IN_POOL
        # VOLATILITY_TAIL, VOLATILITY_THRESHOLD
        # STOCK_PRICE_LOW, STOCK_PRICE_HIGH
        # ADD_THESE_STOCKS, AVOID_THESE_STOCKS
        def get_high_volatility_stocks_price_limited(screener, 
                                                     pool, 
                                                     v_tail, 
                                                     v_thresh, 
                                                     price_l, 
                                                     price_h, 
                                                     add_ts, 
                                                     avoid_ts):
            
            # used to remove low volatility stocks
            def ret_2nd_ele(tuple_1):
                return tuple_1[1]
            
            # volatile stocks list
            volatile_stocks = []
            
            # tuple the useful data (symbol, lastsale, netchange, marketCap)
            for symbol_data in tqdm(screener['data']['table']['rows']):
                
                # capture the close price of the symbol, removing the dollar sigh
                symbol_close_price = symbol_data['lastsale'].replace('$','')
                
                # remove symbols that contain slash, carrot, or space
                if symbol_data['symbol'].find(
                        '^') == -1 and symbol_data['symbol'].find(
                            '/') == -1 and symbol_data['symbol'].find(
                                ' ') == -1: 
                    
                    # get rid of netchange that contain UNCH
                    if symbol_data['netchange'].find('UNCH') == -1:
                        
                        # get rid of marketCap with NA
                        if symbol_data['marketCap'] != 'NA':
                            
                            # only grab stocks between our high and low
                            if float(symbol_close_price) > price_l and float(symbol_close_price) < price_h:
                                
                                # find the volatility of the stock
                                volatility_of_stock = 0.0 - float(symbol_data['netchange'])

                                # top tail, abs, check thresh, 
                                if v_tail == 'TOP' and volatility_of_stock < 0.0:
                                    volatility_of_stock = abs(volatility_of_stock)
                                    if volatility_of_stock > v_thresh:
                                        
                                        # put symbol and volatility in a tuple
                                        symbol_data_tuple = (symbol_data['symbol'], volatility_of_stock)
                                        
                                        # add the tuple to our list
                                        volatile_stocks.append(symbol_data_tuple)
                                        
                                # bottom tail, check thresh
                                elif v_tail == 'BOTTOM' and volatility_of_stock > 0.0:
                                    if float(volatility_of_stock) > v_thresh:
                                        
                                        # put symbol and volatility in a tuple
                                        symbol_data_tuple = (symbol_data['symbol'], volatility_of_stock)
                                        
                                        # add the tuple to our list
                                        volatile_stocks.append(symbol_data_tuple)
            
            symbol_only_list = []
            def extract_symbols(volatile_stock_tuples):
                
                # pull the symbol from the tuple
                for stock in tqdm(volatile_stock_tuples):
                    symbol_only_list.append(stock[0])
                    
                # return the list of symbols only    
                return symbol_only_list
            
            
            # current list has more than what we want NUMBER_OF_STOCKS_IN_POOL
            if len(volatile_stocks) > pool:
                
                # filter down to our number
                # TODO: implement with code below <>
                '''
                pbar = tqdm(total=len(vol_data)-TOP_VOLUME_PREVIOUS_DAY)
                while len(vol_data) > TOP_VOLUME_PREVIOUS_DAY:
                    pbar.set_description('REMOVING_LOW_VOLUME')
                    vol_data.remove(min(vol_data, key=ret_2nd_ele))
                    pbar.update(1)
                pbar.close()
                progress.s('REMOVED_LOWEST_VOLUME_SYMBOLS')
                '''
            
            # report that we have less than what we wanted    
            else:
                progress.w('COUNT:(' + str(len(volatile_stocks)) + ')_NOT_ENOUGH_STOCKS_IN_LIST')
                progress.slowly('The list we have is less than what we want.')
                answer = input('Type YES to use what we have or NO to EXIT. YES or NO: ')
                if answer == 'YES':
                    return extract_symbols(volatile_stocks)
                else:
                    progress.w('(' + answer + ')_EXITING')
                    sys.exit()

        
        # run the filter function and get our stock list
        stocks_to_trade = get_high_volatility_stocks_price_limited(nasdaq_screener_data,
                                                                   NUMBER_OF_STOCKS_IN_POOL,
                                                                   VOLATILITY_TAIL,
                                                                   VOLATILITY_THRESHOLD,
                                                                   STOCK_PRICE_LOW,
                                                                   STOCK_PRICE_HIGH,
                                                                   ADD_THESE_STOCKS,
                                                                   AVOID_THESE_STOCKS,
                                                                   )
        
        ###########################################
        ########  MAIN CASH ACCOUNT LOOP  #########
        ###########################################  
        
        # stop trading when we reach TRADE_CYCLES defined above
        while TRADE_CYCLES > 0:
            
            ###########################################
            ########  RANDOMLY SELECT A SYMBOL  #######
            ###########################################
            
            # generate a random number between 0 and the length of the list
            random_number = random.randrange(len(stocks_to_trade))
            progress.s('GENERATE_RANDOM_NUMBER')
            
            # enumerate our list and randomly select a symbol
            symbol_to_trade = [random_symbol[1] for random_symbol in enumerate(stocks_to_trade) if random_number == random_symbol[0]]
            progress.s('SELECT_RANDOM_SYMBOL')
            progress.w('WE_WILL_TRADE_(' + str(symbol_to_trade[0]) + ')')
            
            ###########################################
            ########  PLACE BUY ORDER  ################
            ###########################################
            
            # buy the random stock
            progress.i('PLACING_AN_ORDER_(buy_random_(' + symbol_to_trade[0] + '))')
            progress.crit(symbol_to_trade[0])
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
                
                # log the DATA
                progress.debug(buy_order_json)
                
                # create a counter to break out of fill loop
                wait_counter = 0
                
                # check to make sure the order filled
                if buy_order_json['filledQuantity'] != 1:
                    
                    # TODO: keep an eye on this
                    while buy_order_json['filledQuantity'] < 1 or wait_counter < 9:
                        
                        while wait_counter < 10:
                            
                            # sleep for 1 second
                            progress.w('WAITING_FOR_FILL_(buy_random_(' + symbol_to_trade[0] + '))')
                            sleep(1)
                            
                            # pull the details of the order
                            get_buy_order = tda_client.get_order(buy_order_id, int(ACCOUNT_ID))
                            
                            # convert the order details to JSON
                            buy_order_json = get_buy_order.json()
                            
                            if buy_order_json['filledQuantity'] == 1:
                                # report successful buy order after waiting for fill
                                progress.s('PLACING_AN_ORDER_(buy_random_(' + symbol_to_trade[0] + '))')
                                progress.crit(buy_order_json['orderActivityCollection'][0]['executionLegs'][0]['price'])
                                wait_counter = 11
                            else:
                                # add to sleep counter
                                wait_counter = wait_counter + 1
                        
                        # fill not successful, cancel the order
                        if wait_counter == 10:
                            cancel_buy_order_response = tda_client.cancel_order(buy_order_id, int(ACCOUNT_ID))
                            cancel_buy_order_json = cancel_buy_order_response.json()                       
                
                            # log the data
                            progress.debug(cancel_buy_order_json)
                else:
                    # report successful buy order when it is automatically filled
                    progress.s('PLACING_AN_ORDER_(buy_random_(' + symbol_to_trade[0] + '))')
                    progress.crit(buy_order_json['orderActivityCollection'][0]['executionLegs'][0]['price'])
                    
            except Exception as err:
                
                # report errors and responses that are caught
                progress.e(f'Unexpected {err=}, {type(err)=} (' + symbol_to_trade[0] + ')') 
                buy_response_error = buy_order_response.json()
                progress.e(buy_response_error)
                
                # remove the stock that causes 'Contact us' error.
                if buy_response_error['error'] == 'Opening transactions for this security must be placed with a broker. Contact us.':
                    stocks_to_trade.remove(symbol_to_trade[0])
            
            ###########################################
            ########  SLEEP BEFORE SELL  ##############
            ###########################################
            
            # sleep for however long we want to hold the stock
            progress.s('SLEEPING_(hold_position_(' + str(HOLD_STOCK_THIS_LONG) + '_seconds))')
            sleep(HOLD_STOCK_THIS_LONG)
            
            ###########################################
            ########  PLACE SELL ORDER  ###############
            ###########################################
            
            # sell the random stock
            progress.i('PLACING_AN_ORDER_(sell_random_(' + symbol_to_trade[0] + '))')
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
                        progress.w('WAITING_FOR_FILL_(sell_random_(' + symbol_to_trade[0] + '))')
                        sleep(1)
                        
                        # pull the details of the order
                        get_sell_order = tda_client.get_order(sell_order_id, int(ACCOUNT_ID))
                        
                        # convert the order details to JSON
                        sell_order_json = get_sell_order.json()
                
                # fill is successful, report it
                progress.s('WAITING_FOR_FILL_(sell_random_(' + symbol_to_trade[0] + '))')
                
                # log the data
                progress.debug(sell_order_json)
            
            except Exception as err:
                progress.e(f'Unexpected {err=}, {type(err)=} (' + symbol_to_trade[0] + ')')
                progress.e(sell_order_response.json())
            progress.s('PLACING_AN_ORDER_(sell_random_(' + symbol_to_trade[0] + '))')
            progress.crit(sell_order_json['orderActivityCollection'][0]['executionLegs'][0]['price'])
            
            # send profit to TRACE, just changed to Decimal, keep an eye on it.
            progress.trace(Decimal(sell_order_json['orderActivityCollection'][0]['executionLegs'][0]['price']
                                   ) - Decimal(buy_order_json['orderActivityCollection'][0]['executionLegs'][0]['price']))

            ###########################################
            ########  SLEEP BEFORE BUY  ###############
            ###########################################
            
            # sleep before we buy another stock
            progress.w('SLEEPING_(ending_cycle(' + str(TRADE_CYCLE_DEFAULT-TRADE_CYCLES+1) + ' of ' + str(TRADE_CYCLE_DEFAULT) + '))')
            sleep(WAIT_BEFORE_BUYING_AGAIN)
            
            
            # decrease TRADE_CYCLES
            TRADE_CYCLES = TRADE_CYCLES - 1
            wait_counter = 0

##############################################################################
######################    APPLICATION SHUTDOWN and EXIT TIMER    #############
##############################################################################
        
        # normal shutdown
        progress.s('APPLICATION_SHUTDOWN_(normal)')
    
    except KeyboardInterrupt:
        
        # kbi shutdown
        progress.s('APPLICATION_SHUTDOWN_(KBInterrupt)')
        
    except Exception as err:
        
        progress.e(f'Unexpected {err=}, {type(err)=} (catch_all_application)')
        
    # Report Application Run Time
    whole_elapsed = time.perf_counter() - s
    progress.w(f"whole_elapsed in {whole_elapsed:0.2f} seconds.")

##############################################################################
######################    RUN MAIN AS FILE (NOT RECOMMENDED)   ###############
##############################################################################
if __name__ == '__main__':
    print('running cli_main() from inside __name__ == __main__')
    cli_main()