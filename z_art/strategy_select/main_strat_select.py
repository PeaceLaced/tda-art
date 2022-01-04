"""
- (main_strat_select.py)

"""

from tda.client import synchronous

class LoadStratTypeException(TypeError):
    '''Raised when there is a type error in :meth:`load_strat`.'''
    
class LoadStratValueException(ValueError):
    '''Raised when there is a value error in :meth:`load_strat`.'''
    
def load_strat(strat, tda_client, symbol_list):
    '''
    Strat selector based on the setting in __main__.
    
    :param strat: defined in :meth:`cli_main` in :file:`__main__`
    :param tda_client: The client object created :meth:`get_client_session` 
                       in :file:`api_td_ameritrade`.
    
    :return: None
    '''
    
    if not isinstance(strat, str):
        raise LoadStratTypeException('strat must be a string')
        
    if not isinstance(tda_client, synchronous.Client):
        raise LoadStratTypeException('tda client object is required')
        
    if not isinstance(symbol_list, list):
        raise LoadStratTypeException('symbol_list must be a list')
    
##### TODO: fine for now, once more strats get added this will not be best solution <>        
    if strat not in {'RANDOM', 'TRIPPLEWIN', 'BASELINE'}:
        raise LoadStratValueException('select the correct strat in __main__')
        
    if strat in {'RANDOM'}:
        from z_art.strategy_select.strat_random.main_strat_random import run_strat_random
        run_strat_random(tda_client, symbol_list)
        
    if strat in {'TRIPPLEWIN'}:
        from z_art.strategy_select.strat_tripplewin.main_strat_tripplewin import run_strat_tripplewin
        run_strat_tripplewin(tda_client, symbol_list)
        
    if strat in {'BASELINE'}:
        from z_art.strategy_select.strat_baseline.main_strat_baseline import run_strat_baseline
        run_strat_baseline(tda_client, symbol_list)
    
    return None