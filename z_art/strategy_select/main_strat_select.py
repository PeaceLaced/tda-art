"""
- (main_strat_select.py)

"""

import sys

from z_art.progress_report.config_progress_report import Progress as progress

def load_strat(strat, tda_client, stocks_to_trade):
    '''
    Strat selector based on the setting in __main__.

    '''
    if strat == 'RANDOM':
        
        # load and run the random strat
        from z_art.strategy_select.strat_random.main_strat_random import run_strat_random
        run_strat_random(tda_client, stocks_to_trade)
        
    elif strat == 'BASELINE':
        
        # load and run the baseline strat
        from z_art.strategy_select.strat_baseline.main_strat_baseline import run_strat_baseline
        run_strat_baseline(tda_client, stocks_to_trade)
        
    else:
        progress.slowly('Please select the correct strategy in __main__')
        progress.w('STRAT_OPTION_(RANDOM)')
        progress.w('STRAT_OPTION_(BASELINE)')
        progress.w('EXITING')
        sys.exit()