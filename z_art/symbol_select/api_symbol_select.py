"""
- (api_symbol_select.py)

"""
import sys
import pytz
import httpx
from tqdm import tqdm
from tda.client import synchronous
from datetime import datetime as dt

from z_art.td_ameritrade.api_td_ameritrade import throttle
from z_art.progress_report.api_progress_report import Progress as progress

class SymbolSelectTypeException(TypeError):
    '''Raised when there is a type error in the symbol select API.'''
    
class SymbolSelectValueException(ValueError):
    '''Raised when there is a value error in the symbol select API.'''
    
def get_nasdaq_screener(full_clean=True, dump_raw=False):
    '''connect to and download the nasdaq screener from api.nasdaq.com/api/screener/stocks
    
    :param full_clean: default is True, removes (NA, slash, carrot, spaces)
    :param dump_raw: default is False, creates an aware datetime tupled with the data
                     - NOT IMPLEMENTED YET (1Jan2022)
                     
    :return: list of symbol data
    '''
##### TODO: list comprehension the appends<>    
    initial_symbol_list = []
    if not isinstance(dump_raw, bool):
        raise SymbolSelectTypeException('dump_raw must be a bool')
    
    if not isinstance(full_clean, bool):
        raise SymbolSelectTypeException('full_clean must be a bool')

    nasdaq_screener_json = httpx.get('https://api.nasdaq.com/api/screener/stocks', 
                                   params={'tableonly' : 'true', 'limit' : 15000,'exchange' : 'all'}, 
                                   headers={"User-Agent": "Mozilla/5.0 (x11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"}
                                   ).json()
    
    asof_trimmed = nasdaq_screener_json['data']['asof'].replace('Last price as of','').replace(',','').split()
    
    new_asof = dt.strptime(asof_trimmed[1] + ' ' + asof_trimmed[0] + ' ' + asof_trimmed[2], "%d %b %Y")
    nasdaq_screener_aware = pytz.timezone('US/Eastern').localize(dt(new_asof.year, new_asof.month, new_asof.day, 20))
    
##### TODO: figure out what to do with this, file, db, etc. <>    
    if dump_raw:
        pass
        #nasdaq_screener_tuple = (nasdaq_screener_json, nasdaq_screener_aware)

    for symbol_data in tqdm(nasdaq_screener_json['data']['table']['rows'], desc='Cleaning Data'): #this is looping through 0, 1, 2, 3...
        if not full_clean:
            initial_symbol_list.append({'symbol':symbol_data['symbol'], 'last_price':symbol_data['lastsale'].replace('$',''), 'net_change':symbol_data['netchange'], 'market_cap':symbol_data['marketCap']})
        else:
            if symbol_data['marketCap'] != 'NA':
                if symbol_data['symbol'].find('^') == -1 and symbol_data['symbol'].find('/') == -1 and symbol_data['symbol'].find(' ') == -1:
                    initial_symbol_list.append({'aware_datetime':nasdaq_screener_aware,
                                                'symbol':symbol_data['symbol'],
                                                'last_price':symbol_data['lastsale'].replace('$',''),
                                                'net_change':symbol_data['netchange'].replace('UNCH', '0.00'),
                                                'market_cap':symbol_data['marketCap'].replace(',', '')})

    return initial_symbol_list

def filter_by_price(symbol_list, price_low, price_high):
    '''return a list of symbol data between price_low and price_high
    
    :param symbol_list: symbol list with attached data
    :param price_low: select stocks greater than this price
    :param price_high: select stocks lower than this price
    
    :return: list of symbol data
    '''
    if not isinstance(symbol_list, list):
        raise SymbolSelectTypeException('symbol_list must be a list')
        
    if not isinstance(price_low, float):
        raise SymbolSelectTypeException('price_low must be a float')
        
    if not isinstance(price_high, float):
        raise SymbolSelectTypeException('price_high must be a float')
        
    filtered_price_symbols = []
    for symbol_data in tqdm(symbol_list, desc='Applying Price Filter'):
        if float(symbol_data['last_price']) > price_low:
            if float(symbol_data['last_price']) < price_high:
                filtered_price_symbols.append(symbol_data)
    symbol_list.clear()
    
    return filtered_price_symbols

def filter_by_netchange(symbol_list, net_direction, net_thresh):
    '''return a list of symbol data within net_change params
    
    :param symbol_list: symbol list with attached data
    :param net_direction: net change in the positve or negative direction
    :param net_thresh: the amount of change
                       POSITIVE net_direction is above net_thresh
                       NEGATIVE net_direction is below negative net_thresh
    
    :return: list of symbol data
    '''
    
    if not isinstance(symbol_list, list):
        raise SymbolSelectTypeException('symbol_list must be a list')
        
    if not isinstance(net_direction, str):
        raise SymbolSelectTypeException('net_direction must be a string')
        
    if not isinstance(net_thresh, float):
        raise SymbolSelectTypeException('net_thresh must be a float')
        
    if net_direction not in {'POSITIVE', 'NEGATIVE'}:
        raise SymbolSelectValueException('net_direction must be either POSITIVE or NEGATIVE')
        
    filtered_netchange_symbols = []
    for symbol_data in tqdm(symbol_list, desc='Applying Netchange Filter'):
        if net_direction in {'POSITIVE'}:
            if float(symbol_data['net_change']) >= net_thresh:
                filtered_netchange_symbols.append(symbol_data)
 
        if net_direction in {'NEGATIVE'}:
            if float(symbol_data['net_change']) <= (0 - net_thresh):
                filtered_netchange_symbols.append(symbol_data)

    return filtered_netchange_symbols

def filter_by_top_marketcap(symbol_list, cap_thresh):
    '''return a list of symbol data within market_cap params
    
    :param symbol_list: symbol list with attached data
    :param cap_thresh: market cap will be greater than this number
    
    :return: list of symbol data
    '''
    if not isinstance(symbol_list, list):
        raise SymbolSelectTypeException('symbol_list must be a list')
        
    if not isinstance(cap_thresh, int):
        raise SymbolSelectTypeException('cap_thresh must be an int')
         
    filtered_marketcap_symbols = []
    for symbol_data in tqdm(symbol_list, desc='Applying Marketcap Filter'):
        if int(symbol_data['market_cap']) > cap_thresh:
            filtered_marketcap_symbols.append(symbol_data)
    
    return filtered_marketcap_symbols

def filter_by_top_volume(tda_client, symbol_list, volume_thresh):
    '''return a list of symbol data within volume params
    
    :param tda_client: The client object created by tda-api.
    :param symbol_list: symbol list with attached data
    :param volume_thresh: volume will be greater than this number
    
    :return: list of symbol data
    '''
    if not isinstance(tda_client, synchronous.Client):
        raise SymbolSelectTypeException('tda client object is required')
    
    if not isinstance(symbol_list, list):
        raise SymbolSelectTypeException('symbol_list must be a list')
        
    if not isinstance(volume_thresh, int):
        raise SymbolSelectTypeException('volume_thresh must be an int')
    
    if len(symbol_list) > 120:
        report_time = len(symbol_list)*0.7
    else:
        report_time = 10
        
    progress.slowly('Volume filter for ' + str(len(symbol_list)) + ' stocks will take ~' + str(report_time) +  ' seconds to process.')
    progress.slowly('YES to continue, NO to exit, SKIP to bypass.')
    
    continue_input = input().upper()
    if continue_input in {'YES'}:
        filtered_volume_symbols = []
        for symbol_data in tqdm(symbol_list, desc='Getting Volume Data'):
            r = tda_client.get_price_history(symbol_data['symbol'],
                                             period_type=tda_client.PriceHistory.PeriodType.MONTH,
                                             period=tda_client.PriceHistory.Period.ONE_MONTH,
                                             frequency_type=tda_client.PriceHistory.FrequencyType.DAILY,
                                             frequency=tda_client.PriceHistory.Frequency.DAILY,
                                             need_extended_hours_data=False)
            
            if isinstance(r, httpx.Response):
                if r.status_code in {200, 201, 202}:
                    try:
                        symbol_volume = r.json()['candles'].pop()['volume']
                        if symbol_volume > volume_thresh:
                            filtered_volume_symbols.append({'aware_datetime':symbol_data['aware_datetime'],
                                                            'symbol':symbol_data['symbol'], 
                                                            'last_price':symbol_data['last_price'],
                                                            'net_change':symbol_data['net_change'],
                                                            'market_cap':symbol_data['market_cap'],
                                                            'volume':symbol_volume})
                    except Exception as err:
                        # TODO: should we remove the symbol if it fails volume data check <>
                        pass

            if len(symbol_list) > 120:
                throttle(0.5)
            
        return filtered_volume_symbols
    
    if continue_input in {'SKIP'}:
        return symbol_list
    
    if continue_input in {'NO'}:
        progress.w('EXITING')
        sys.exit()


def final_symbol_filter(symbol_list, add_avoid=False, strip_data=True):
    '''returns the final symbol list based on params
    
    :param symbol_list: symbol list with attached data
    :param manual_add: takes a list and adds the symbols 
                       default is False, True only works if strip_data=True
    :param manual_avoid: takes a list and removes the symbols 
                         default is False, True only works if strip_data=True
    :param strip_data: remove all data and return ONLY the symbol list
    
    :return: symbol list with or without data attached
    '''
        
    if not isinstance(symbol_list, list):
        raise SymbolSelectTypeException('symbol_count must be a list')
        
    if not isinstance(strip_data, bool):
        raise SymbolSelectTypeException('strip_data must be a bool')
        
    if not isinstance(add_avoid, bool):
        if not isinstance(add_avoid, tuple):
            raise SymbolSelectTypeException('add_avoid must be a bool or tuple')
    
    if not isinstance(add_avoid[0], list):
        raise SymbolSelectTypeException('add_avoid[0] must be a list')
        
    if not isinstance(add_avoid[1], list):
        raise SymbolSelectTypeException('add_avoid[1] must be a list')
    
    final_symbol_list = []

    if strip_data:
        for symbol_data in symbol_list:
            final_symbol_list.append(symbol_data['symbol'])
            
        if add_avoid[0]:
            for symbol_to_add in add_avoid[0]:
                if symbol_to_add in final_symbol_list:
                    final_symbol_list.append(symbol_to_add)
        
        if add_avoid[1]:
            for symbol_to_avoid in add_avoid[1]:
                if symbol_to_avoid in final_symbol_list:
                    final_symbol_list.remove(symbol_to_avoid)
                    
    if not strip_data:
        final_symbol_list = symbol_list
        
    return final_symbol_list