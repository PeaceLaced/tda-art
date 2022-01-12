"""
- (main_symbol_select.py)

"""

from tda.client import synchronous
from z_art.symbol_select import api_symbol_select as api

class GetSymbolTypeException(TypeError):
    '''Raised when there is an :error:`TypeError` in :meth:`get_symbols`.'''
    
def get_symbols(tda_client):
    '''
    generates a symbol list for trading, :meth:`get_nasdaq_screener`  is required
                                         :meth:`final_symbol_filter` is required for 
                                                                     a symbol only list
    NOTICE: :meth:`filter_by_volume` should be called after all other methods
                                     but before :meth:`final_symbol_filter` 
                                     because it connects to TDA at 0.5 seconds
                                     per symbol. Less symbols = Less time.
    
    :param tda_client: The client object created by tda-api.
                       Required, even if not using :meth:`filter_by_top_volume`
    
    return: a list of symbols based on whatever filter functions are called
    '''
    if not isinstance(tda_client, synchronous.Client):
        raise GetSymbolTypeException('tda client object required')
    
    symbol_list = api.get_nasdaq_screener(full_clean=True)
    
    symbol_list = api.filter_by_price(symbol_list, 2.00, 7.00)
    
    symbol_list = api.filter_by_netchange(symbol_list, 'POSITIVE', 0.04) # min net change
    
    symbol_list = api.filter_by_top_marketcap(symbol_list, 50000000) # 50 Million
    
    symbol_list = api.filter_by_top_volume(tda_client, symbol_list, 500000) # 500 Thousand
    
    ADD_AVOID = ([], ['ARDS', 'TUYA', 'ARMP'])
    
    symbol_list = api.final_symbol_filter(symbol_list, add_avoid=ADD_AVOID, strip_data=True)
    
    return symbol_list
