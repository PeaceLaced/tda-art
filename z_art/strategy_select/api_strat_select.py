"""
- (api_strat_select.py)

"""
import httpx
from copy import deepcopy
from enum import Enum
from time import sleep
from tda.utils import Utils
from tda.client import synchronous
from decimal import Decimal, setcontext, BasicContext
from tda.orders.equities import equity_buy_market, equity_sell_market
from z_art.td_ameritrade.api_td_ameritrade import ACCOUNT_ID

# slowly converting everyting to the new API
from z_art.progress_report.api_progress_report import Progress as progress
from z_art.td_ameritrade.api_td_ameritrade import throttle

# set decimal context, precision = 9, rounding = round half even
setcontext(BasicContext)

class OrderType(Enum):
    '''Used when placing orders and in other logic for standardization.'''
    BUY = 'BUY'
    SELL = 'SELL'
    PROFIT = 'PROFIT'

class StratSelectTypeException(TypeError):
    '''Raised when there is a type error in :file:`api_strat_select`.'''
    
class StratSelectValueException(ValueError):
    '''Raised when there is a value error in :file:`api_strat_select`.'''
    
class DataSyndicateTypeException(TypeError):
    '''Raised when there is a type error in :meth:`data_syndicate`'''

def _order_report(order_data, order_type=False, order_symbol=False, order_shares=False):
    '''Used by methods that set order_report=True

    :param order_data: can be order_json (`order_get_details`)
                       or an order_response (`order_place_equity_market`)
    :param order_type: default is False, REQUIRED when order_data is httpx.Response
    :param order_symbol: default is False, REQUIRED when order_data is httpx.Response
    :param order_shares: default is False, REQUIRED when order_data is httpx.Response
    '''
    if not isinstance(order_data, (dict, httpx.Response)):
        raise StratSelectTypeException('order_data should be an order_json dict or httpx.Reponse object')
    
    if isinstance(order_data, dict):
        order_type = str(order_data['orderLegCollection'][0]['instruction'])
        order_symbol = str(order_data['orderLegCollection'][0]['instrument']['symbol'])
        order_shares = str(int(order_data['quantity']))
        if int(order_data['quantity']) == int(order_data['filledQuantity']):
            #MARKET_ORDER_FILLED_(BUY_(AAPL, 25))
            progress.s('MARKET_ORDER_FILLED_(' + order_type + '_(' + order_symbol + ', ' + order_shares +'))')
        if int(order_data['quantity']) != int(order_data['filledQuantity']):
            #WAITING_FOR_FILL_(BUY_(AAPL, 25))
            progress.w('WAITING_FOR_FILL_(' + order_type + '_(' + order_symbol + ', ' + order_shares +'))')
    
##### TODO: this is a duplicate, it is being handled twice, keep for now (3Jan2022) <>
    if isinstance(order_data, httpx.Response):
        
        if not order_type:
            raise StratSelectValueException('passing order_response requires order_type to be set')
        if not isinstance(order_type, OrderType):
            raise StratSelectTypeException('order_type must be of type OrderType')
        if isinstance(order_type, OrderType.BUY):
            order_type = OrderType.BUY.value
        if isinstance(order_type, OrderType.SELL):
            order_type = OrderType.SELL.value
            
        if not order_symbol:
            raise StratSelectValueException('passing order_response requires order_symbol to be set')
            
        if not order_shares:
            raise StratSelectValueException('passing order_response requires order_shares to be set')
            
        if isinstance(order_symbol, str):
            order_symbol = order_symbol
        if isinstance(order_shares, int):
            order_shares = str(order_shares)
        #PLACING_MARKET_ORDER_(BUY_(AAPL, 25))
        progress.i('PLACING_MARKET_ORDER_(' + order_type + '_(' + order_symbol + ', ' + order_shares +'))')
    
def order_get_details(tda_client, order_response, wait_for_fill=False, order_report=False):
##### TODO: create a RAW log in progress_report <>
##### TODO: think about using a tuple for wait_for_fill (sec_to_wait, sec_between_wait)
    ''' Get the detials of an order

    :param tda_client: The client object created by tda-api.
    :param `order_response`: The response object from a TDA order.
                           An order ID may also be passed.
    :param `wait_for_fill`: default is False, wait `int` seconds before canceling the order.
                          Passing True (or 1) will wait for fill indefinetly.
                          Checks status every 1 second (see wait_for_fill TODO:)
    :param `order_report`: default is False, 
                           True: reports fill status to MAIN
                                 and dumps raw json to DEBUG
    '''
    if not isinstance(tda_client, synchronous.Client):
        raise StratSelectTypeException('tda client object required to get order details')
    
    if order_response is None:
        raise StratSelectValueException('at least one, an order response or ID, must be passed')
        
    if isinstance(order_response, httpx.Response):
        order_response = Utils(tda_client, int(ACCOUNT_ID)).extract_order_id(order_response)
        throttle(0.3)
    
    if isinstance(order_response, int):
        order_json = tda_client.get_order(order_response, int(ACCOUNT_ID)).json()
        throttle(0.3)
        
    if isinstance(order_json['orderLegCollection'][0]['instrument']['symbol'], str):
        order_symbol = order_json['orderLegCollection'][0]['instrument']['symbol']
        
    if wait_for_fill: # everything but False
        if not isinstance(wait_for_fill, int): # cap non True/int
            raise StratSelectTypeException('wait for fill must be False, True, or an int')
        else: # True and int
            cycle_count = 0

            while int(order_json['quantity']) != int(order_json['filledQuantity']):
                if cycle_count < wait_for_fill:
                    if order_report:
                        _order_report(order_json)
                    sleep(1)
                    order_json = tda_client.get_order(order_response, int(ACCOUNT_ID)).json()
                    if wait_for_fill != 1:
                        cycle_count = cycle_count + 1
                    else:
                        pass # wait for fill indefinetly (useful mostly when selling)
                else:
                    try:
######################### TODO: think about how to handle symbols that do not fill, possible removal, see remove_symbol()
                        order_response = tda_client.cancel_order(order_json['orderId'], int(ACCOUNT_ID))
                        order_json = order_response.json()
                    except Exception as err:
######################### TODO: what exceptions can we expect here, to catch and handle properly
                        progress.e(f'Unexpected {err=}, {type(err)=} (order_response)_(' + order_symbol + ')')
                        progress.e(('order_response', order_response))
                        order_json = order_response.json()
                        progress.e(('order_json', order_json))
            if int(order_json['quantity']) == int(order_json['filledQuantity']):
                if order_report:
                    _order_report(order_json)
                    
    if order_report:
        progress.debug(order_json)
    
    return order_json

def order_place_equity_market(tda_client, order_type, order_symbol, order_shares, order_report=False):
    ''' Place an equity market order, either buy or sell.

    :param tda_client: The client object created by tda-api.
    :param order_type: BUY or SELL
    :param order_symbol: the symbol to buy or sell
    :param order_shares: share quantity to buy or sell
    :param order_report: default is False, when True, dumps a raw json to the MAIN log
    
    :return: order_response, to extract order details USE :meth:`order_get_details` 
    '''
    if not isinstance(tda_client, synchronous.Client):
        raise StratSelectTypeException('tda_client object required to place an order')
        
    if not isinstance(order_type, OrderType):
        raise StratSelectTypeException('order type must be OrderType.BUY/OrderType.SELL')
       
    if not isinstance(order_shares, int) or order_shares < 1:
        raise StratSelectValueException('order shares must be an int that is greater than zero')
    
    if isinstance(order_type, OrderType) and order_type == OrderType.BUY:
        order_response = tda_client.place_order(int(ACCOUNT_ID), equity_buy_market(order_symbol, order_shares))
     
    if isinstance(order_type, OrderType) and order_type == OrderType.SELL:
        order_response = tda_client.place_order(int(ACCOUNT_ID), equity_sell_market(order_symbol, order_shares))
     
    if isinstance(order_response, httpx.Response):
        if order_response.status_code not in {200, 201, 202}:
            progress.e((order_response.status_code, order_response))
        elif order_report:
            _order_report(order_response, order_type, order_symbol, order_shares)
          
    return order_response

buy_list = []
sell_list = []
profit_list = []
def data_syndicate(data_point, report_data=False, report_lists=False, report_profit=False, return_profit=False):
    ''' 
    Turn BUY and SELL items into PROFIT 
    - primairly used for turning data points into a profit format 
      useful for further processing (ie. a spreadsheet, another function, etc.)
    
    :param data_point: takes an order_response json file.
    :param report_data: default is False.
                          - True reports every datapoint as it is consumed
                          - reports to Trace Log
    :param report_lists: default is False.
                          - True reports BUY and SELL lists
                            after they have been fully realized
                          - reports to Error Log
    :param report_profit: default is False.
                          - True reports PROFIT after it has been calculated
                          - reports to Trace Log
    :param return_profit: default is False. 
                          True returns a list of tuples (symbol, profit)
    
    :return: depends
    '''
    if not isinstance(data_point, dict):
        raise DataSyndicateTypeException('data_point must be of type dict (an order_json)')

    if not isinstance(report_data, bool):
        raise DataSyndicateTypeException('report_data must be of type bool')
    
    if not isinstance(report_lists, bool):
        raise DataSyndicateTypeException('report_lists must be of type bool')
    
    if not isinstance(report_profit, bool):
        raise DataSyndicateTypeException('report_profit must be of type bool')
    
    if not isinstance(return_profit, bool):
        raise DataSyndicateTypeException('return_profit must be of type bool')
    
    order_type = data_point['orderLegCollection'][0]['instruction']
    if not isinstance(order_type, str):
        raise DataSyndicateTypeException('the extracted order_type is not a string')
        
    order_symbol = data_point['orderLegCollection'][0]['instrument']['symbol']
    if not isinstance(order_symbol, str):
        raise DataSyndicateTypeException('the extracted order_symbol is not a string')
    
    order_price = data_point['orderActivityCollection'][0]['executionLegs'][0]['price']
    if not isinstance(order_price, float):
        raise DataSyndicateTypeException('the extracted order_price is not a float')
    
    data_point = (order_type, order_symbol, str(order_price))
    if not isinstance(data_point, tuple):
        raise DataSyndicateTypeException('the newly created data_point is not a tuple')
    
    if data_point[0] == OrderType.BUY.value:
        buy_list.append(data_point)
        if report_data:
            progress.trace(data_point[0] + ' | ' + data_point[1] + ' | ' + data_point[2] + ' | ')
        return None
    if data_point[0] == OrderType.SELL.value:
        sell_list.append(data_point)
        if report_data:
            progress.trace(data_point[0] + ' | ' + data_point[1] + ' | ' + data_point[2] + ' | ')
        if len(buy_list) == len(sell_list):
            for buy_item in buy_list:
                for sell_item in sell_list:
                    if buy_item[1] == sell_item[1]:
                        profit = Decimal(sell_item[2]) - Decimal(buy_item[2])
                        profit_list.append((sell_item[1], str(profit)))
                        if report_profit:
                            progress.trace(OrderType.PROFIT.value + ' | ' + str(sell_item[1]) + ' | ' + str(profit) + ' | ')
            # removed list reporting to progress.e (3Jan2022)
            if not return_profit:
                buy_list.clear()
                sell_list.clear()
                profit_list.clear()
                return None
            if return_profit:
                temp_profit_list = deepcopy(profit_list)
                buy_list.clear()
                sell_list.clear()
                profit_list.clear()
                return temp_profit_list

def remove_symbol():
    '''we need something that removes symbols from the main symbol list
    '''
##### TODO: need to work on this soon, remove problem symbols from the main symbol list <>    
    pass
