"""
- (main_symbol_select.py)

"""

import sys
#import pytz
import requests

from tqdm import tqdm
#from datetime import datetime as dt
from decimal import setcontext, BasicContext, Decimal

from z_art.progress_report.config_progress_report import Progress as progress

# basic context is decimal precision = 9 and rounding = round half even
setcontext(BasicContext)

def get_nasdaq_screener(aware_dt=False):
    '''
    Returns a raw data object from api.nasdaq.com/api/screener/stocks
    - called from :meth:`get_high_volatility_stocks_price_limited`
    
    '''
    # Get the NEW nasdaq screener from API and convert it to JSON
    nasdaq_screener_nowpull = requests.get('https://api.nasdaq.com/api/screener/stocks', 
                                           params={'tableonly' : 'true', 'limit' : 15000,'exchange' : 'all'}, 
                                           headers={"User-Agent": "Mozilla/5.0 (x11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"}
                                           ).json()
    
    # Use asof date to create aware datetime
    #asof_trimmed = nasdaq_screener_nowpull['data']['asof'].replace('Last price as of','').replace(',','').split()
    #new_asof = dt.strptime(asof_trimmed[1] + ' ' + asof_trimmed[0] + ' ' + asof_trimmed[2], "%d %b %Y")
    #ns_nowpull_aware_datetime = pytz.timezone('US/Eastern').localize(dt(new_asof.year, new_asof.month, new_asof.day, 20))

    #return ns_nowpull_aware_datetime

    return nasdaq_screener_nowpull

# function that takes in the variables and returns a list of symbols to trade
def get_high_volatility_stocks_price_limited(screener, 
                                             pool, 
                                             v_tail, 
                                             v_thresh, 
                                             v_cut,
                                             price_l, 
                                             price_h):

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
                        volatility_of_stock = Decimal(0.0) - Decimal(symbol_data['netchange'])

                        # top tail, abs, check thresh, 
                        if v_tail == 'POSITIVE' and volatility_of_stock < 0.0:
                            volatility_of_stock = abs(volatility_of_stock)
                            if volatility_of_stock > v_thresh:
                                
                                # put symbol and volatility in a tuple
                                symbol_data_tuple = (symbol_data['symbol'], volatility_of_stock)
                                
                                # add the tuple to our list
                                volatile_stocks.append(symbol_data_tuple)
                                
                        # bottom tail, check thresh
                        elif v_tail == 'NEGATIVE' and volatility_of_stock > 0.0:
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
         
    # used to remove low volatility stocks
    def ret_2nd_ele(tuple_1):
        return tuple_1[1]
    
    # sorting method for trace reporting volatile stocks
    def trace_report_sorted_stock_list(stock_list):
        for each_stock in sorted(stock_list):
            progress.trace('volatility | ' + str(each_stock[0]) + ' | ' + str(each_stock[1]) + ' |')
        return
     
    # after filtering by price, tail, and volatility threshold
    # select the top, bottom or center based on POOL
    # TODO: Clean this whole thing up to remove duplication <>
    if len(volatile_stocks) > pool:
        
        # remove using min (removes the lowest volatility, leaving the TOP)
        if v_cut == 'TOP':
            while len(volatile_stocks) != pool:
                volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                if len(volatile_stocks) == pool:
                    break
        
        # remove using max (removes the highest volatility, leaving the BOTTOM)
        elif v_cut == 'BOTTOM':
            while len(volatile_stocks) != pool:
                volatile_stocks.remove(max(volatile_stocks, key=ret_2nd_ele))
                if len(volatile_stocks) == pool:
                    break
                
        # remove the top and bottom of the highest volatility, leaving the center
        elif v_cut == 'CENTER':
            
            # figure out if what we want and what we got is even or odd
            if pool % 2 == 0 and len(volatile_stocks) % 2 == 0:
                
                # these are even, even, just take one from each side
                progress.i('EVEN_EVEN')
                while len(volatile_stocks) != pool:
                    volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                    volatile_stocks.remove(max(volatile_stocks, key=ret_2nd_ele))
                    if len(volatile_stocks) == pool:
                        break
                
            elif pool % 2 == 0 and len(volatile_stocks) % 2 == 1:
                
                #these are even, odd, remove one bottom, then take one from each side
                progress.i('EVEN_ODD')
                volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                while len(volatile_stocks) != pool:
                    volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                    volatile_stocks.remove(max(volatile_stocks, key=ret_2nd_ele))
                    if len(volatile_stocks) == pool:
                        break
                
            elif pool % 2 == 1 and len(volatile_stocks) % 2 == 1:
                
                # these are odd, odd, just take one from each side
                progress.i('ODD_ODD')
                while len(volatile_stocks) != pool:
                    volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                    volatile_stocks.remove(max(volatile_stocks, key=ret_2nd_ele))
                    if len(volatile_stocks) == pool:
                        break
                    
            elif pool % 2 == 1 and len(volatile_stocks) % 2 == 0:
                
                # these are odd even, take one from bottom then remove each side
                progress.i('ODD_EVEN')
                volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                while len(volatile_stocks) != pool:
                    volatile_stocks.remove(min(volatile_stocks, key=ret_2nd_ele))
                    volatile_stocks.remove(max(volatile_stocks, key=ret_2nd_ele))
                    if len(volatile_stocks) == pool:
                        break
        
        # after breaking out, verify what we have is what we want
        volatility_low_point = min(volatile_stocks, key=ret_2nd_ele)
        volatility_high_point = max(volatile_stocks, key=ret_2nd_ele)
        progress.w('VOLATILITY_IS_BETWEEN_(' + str(volatility_low_point[1]) + ' and ' + str(volatility_high_point[1]) + ')')
        progress.slowly('Stocks to trade are between these two volatility points: ' + str(volatility_low_point[1]) + ' and ' + str(volatility_high_point[1]))
        answer = input('Type YES to use what we have or NO to EXIT. YES or NO: ')
        
        if answer == 'YES':
            
            # trace report an alphabetized volatile stock list
            trace_report_sorted_stock_list(volatile_stocks)
            
            # progress report that we are continuing to the trade sequence
            progress.w('(' + answer + ')_CONTINUING')
            
            # extract the symbols and return the list for trading 
            return extract_symbols(volatile_stocks)
        
        else:
            progress.w('(' + answer + ')_EXITING')
            sys.exit()
                                  
    # report that we have less than what we wanted    
    else:
        # after breaking out, verify what we have is what we want
        volatility_low_point = min(volatile_stocks, key=ret_2nd_ele)
        volatility_high_point = max(volatile_stocks, key=ret_2nd_ele)
        progress.w('VOLATILITY_IS_BETWEEN_(' + str(volatility_low_point[1]) + ' and ' + str(volatility_high_point[1]) + ')')
        progress.w('COUNT:(' + str(len(volatile_stocks)) + ')_NOT_ENOUGH_STOCKS_IN_LIST')
        progress.slowly('The list we have is less than what we want.')
        answer = input('Type YES to use what we have or NO to EXIT. YES or NO: ')
        if answer == 'YES':
            
            # trace report an alphabetized volatile stock list
            trace_report_sorted_stock_list(volatile_stocks)
            
            # progress report that we are continueing to the trade sequence
            progress.w('(' + answer + ')_CONTINUING')
            
            # extract the symbols and return the list for trading 
            return extract_symbols(volatile_stocks)
        else:
            progress.w('(' + answer + ')_EXITING')
            sys.exit()


# returns a list of symbols to trade based on settings in config_symbol_select.py
def get_symbols():
    
    # grab the nasdaq screener, grab the data to pass into our top volatility/price limit function
    ns = get_nasdaq_screener()
    nasdaq_screener_data = ns
    
    # load variables from config file
    from z_art.symbol_select.config_symbol_select import STOCK_PRICE_LOW, STOCK_PRICE_HIGH
    from z_art.symbol_select.config_symbol_select import VOLATILITY_TAIL, VOLATILITY_THRESHOLD
    from z_art.symbol_select.config_symbol_select import VOLATILITY_CUT, NUMBER_OF_STOCKS_IN_POOL
    from z_art.symbol_select.config_symbol_select import ADD_THESE_STOCKS, AVOID_THESE_STOCKS

    # report the variables being used
    progress.w('(' + str(STOCK_PRICE_LOW) + ')_STOCK_PRICE_LOW')
    progress.w('(' + str(STOCK_PRICE_HIGH) + ')_STOCK_PRICE_HIGH')

    progress.w('(' + str(VOLATILITY_TAIL) + ')_VOLATILITY_TAIL')
    progress.w('(' + str(VOLATILITY_THRESHOLD) + ')_VOLATILITY_THRESHOLD')

    progress.w('(' + str(VOLATILITY_CUT) + ')_VOLATILITY_CUT')
    progress.w('(' + str(NUMBER_OF_STOCKS_IN_POOL) + ')_NUMBER_OF_STOCKS_IN_POOL')

    progress.w('(' + str(len(ADD_THESE_STOCKS)) + ')_ADDING_THIS_COUNT')
    progress.w('(' + str(len(AVOID_THESE_STOCKS)) + ')_REMOVING_THIS_COUNT')

    # run the filter function and get our stock list
    stocks_to_trade = get_high_volatility_stocks_price_limited(nasdaq_screener_data,
                                                               NUMBER_OF_STOCKS_IN_POOL,
                                                               VOLATILITY_TAIL,
                                                               VOLATILITY_THRESHOLD,
                                                               VOLATILITY_CUT,
                                                               STOCK_PRICE_LOW,
                                                               STOCK_PRICE_HIGH
                                                               )
    
    # push ADD and AVOID to the list before we start trading
    # this adds or takes away from total POOL
    if len(ADD_THESE_STOCKS) > 0:
        for add_symbol in ADD_THESE_STOCKS:
            stocks_to_trade.append(add_symbol)
    if len(AVOID_THESE_STOCKS) > 0:        
        for remove_symbol in AVOID_THESE_STOCKS:
            if remove_symbol in stocks_to_trade:
                stocks_to_trade.remove(remove_symbol)
    
    # return our list of stocks            
    return stocks_to_trade
