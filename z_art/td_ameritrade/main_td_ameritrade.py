"""
- (main_td_ameritrade.py)

"""

import sys

from z_art.progress_report.config_progress_report import Progress as progress
from z_art.td_ameritrade.config_td_ameritrade import TOKEN_PATH, API_KEY_TDA, ACCOUNT_ID

def get_client_session():
    '''
    Returns a tda-api asyncio client session for use throughout the program.
    
    TDA-API DOCS:     https://tda-api.readthedocs.io/en/latest/
    TDA-API SOURCE:   https://github.com/alexgolec/tda-api
    TDA-API DISCORD:  https://discord.gg/M3vjtHj
    
    '''
    # create an authenticated TDA client session using TDA-API.
    progress.i('TDA_TOKEN_(search)')
    try:
        
        # import and create an authenticated TDA client session
        from tda.auth import client_from_token_file
        tda_client = client_from_token_file(TOKEN_PATH, API_KEY_TDA)
    
    # create TDA token and client session if token file is not found
    except FileNotFoundError:
        
        # TODO: think about adding another try/except here <>
        progress.w('TDA_TOKEN_(not_found)')
        from selenium import webdriver
        from tda.auth import client_from_login_flow
        from .config import REDIRECT_URI
        
        progress.i('TDA_TOKEN_(create)')
        with webdriver.Firefox() as DRIVER:
            tda_client = client_from_login_flow(
                DRIVER, API_KEY_TDA, REDIRECT_URI, TOKEN_PATH)
    
    # catch errors, report and exit
    except Exception as err:
        progress.e(f'Unexpected {err=}, {type(err)=} (catch_all_tda-api)')
        progress.w('EXITING')
        sys.exit()
    
    # report success
    progress.s('TDA_TOKEN_(found)')
    
    return tda_client
def get_my_balance(connection):
    '''
    Logs some TD Ameritrade account info.
    - Account Type
    - Cash Available
    
    '''
    # get account information from TDA and convert to json
    account_info = connection.get_account(int(ACCOUNT_ID)).json()
    
    # get account type from the account information
    tda_account_type = account_info['securitiesAccount']['type']
    progress.i('TDA_ACCOUNT_(TYPE: ' + str(tda_account_type) + ')')
    
    # get cash available for trading
    cash_available_for_trading = account_info['securitiesAccount']['currentBalances']['cashAvailableForTrading']
    progress.w('TDA_ACCOUNT_(CASH: ' + str(cash_available_for_trading) + ')')