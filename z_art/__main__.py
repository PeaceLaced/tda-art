"""
- Set the STRATEGY.

"""
import sys
import time
from z_art.strategy_select.main_strat_select import load_strat
from z_art.symbol_select.main_symbol_select import get_symbols

# slowly converting everyting to the new API
from z_art.progress_report.api_progress_report import Progress as progress
from z_art.td_ameritrade.api_td_ameritrade import get_client_session, get_my_balance

async def cli_main():
    '''
    Main application logic, set strat here.
    
    '''
    try:
        
        # pick a strat (RANDOM, TRIPPLEWIN, BASELINE)
        strat = 'RANDOM'
        
        # create a performance counter
        s = time.perf_counter()
        
        # clear the CLI
        progress.clearly()
        
        # create a tda-api client session
        tda_client = get_client_session()
        
        # get TD Ameritrade account details
        get_my_balance(tda_client)
        
        # select the symbols we want to trade
        stocks_to_trade = get_symbols(tda_client)
        
        # load and run the strat
        load_strat(strat, tda_client, stocks_to_trade)
        
        # calculate and report application runtime
        app_time_elapsed = time.perf_counter() - s
        progress.w(f"whole_elapsed in {app_time_elapsed:0.2f} seconds.")
        
        # report normal shutdown
        progress.s('APPLICATION_SHUTDOWN_(normal)')
    
    except KeyboardInterrupt:
        
        # report keyboard interrupt shutdown
        progress.w('APPLICATION_SHUTDOWN_(KBInterrupt)')
      
    except Exception as err:
        
        # report exception thrown and exit
        progress.e(f'Unexpected {err=}, {type(err)=} (catch_all_application)')
        progress.w('EXITING')
        sys.exit()

# RUN __main__ as a file (NOT RECOMMENDED)
if __name__ == '__main__':
    print('running cli_main() from inside __name__ == __main__')
    cli_main()