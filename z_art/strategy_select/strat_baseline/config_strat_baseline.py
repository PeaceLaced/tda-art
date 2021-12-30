"""
- Settings for Baseline Strat.

"""

##############################################################################
#######    Control variables for the BASELINE Strategy                ########
#######    -------------------------------------------                ########
#######    I call this the Tripple-WIN BASELINE strategy              ########
#######    It buys a share for every stock, then sells it (PRE)       ########
#######    If profit is negative or zero, the symbol is removed       ########
#######    It does this three times, then begins its normal loop      ########
##############################################################################

##############################################################################
####                                                                      ####
####    MINUTES_TO_RUN  how many minutes do we want to run our script     ####
####    -------------------------------------------------------------     ####
####    for easy control on runtime (360 MAX, 330 recommended)            ####
####                                                                      ####
MINUTES_TO_RUN = 60                                                       ####
##############################################################################

##############################################################################
####                                                                      ####
####    STOP_TRYING_TO_BUY  how long do we wait for fill before canceling ####
####    ----------------------------------------------------------------- ####
####    reflected in seconds, only on the BUY                             ####
####                                                                      ####
STOP_TRYING_TO_BUY = 10                                                   ####
##############################################################################

# NOTE: this strat will ONLY work with one share, do NOT incrase this number
##############################################################################
####                                                                      ####
####    HARDCODED_TEST_SHARES   how many shares bought/sold during PRE    ####
####    --------------------------------------------------------------    ####
####    It is NOT advised to use more than one share during PRE           ####
####                                                                      ####
HARDCODED_TEST_SHARES = 1                                                 ####
##############################################################################

# NOTE: this strat will ONLY work with one share, do NOT incrase this number
##############################################################################
####                                                                      ####
####    TRIPPLE_WIN_SHARES  how many shares to trade during Tripple-WIN   ####
####    ---------------------------------------------------------------   ####
####    Stick with one share because this strategy loves to bleed money   ####
####                                                                      ####
TRIPPLE_WIN_SHARES = 1                                                    ####
##############################################################################

##############################################################################
####                                                                      ####
####    HOLD_STOCK_THIS_LONG  how long do you want to hold after buy      ####
####    ------------------------------------------------------------      ####
####    Represented in seconds                                            ####
####                                                                      ####
HOLD_STOCK_THIS_LONG = 50                                                 ####
##############################################################################

##############################################################################
####                                                                      ####
####    TRIPPLE_WIN_MOD     modifier for tripple-win sleep                ####
####    -----------------------------------------------------------       ####
####    In seconds, MOD times the number of stocks trading is sleep       ####
####                                                                      ####
TRIPPLE_WIN_MOD = 60                                                      ####
##############################################################################
# TODO: Think more about how to more accurately represent our sleep cycle <>