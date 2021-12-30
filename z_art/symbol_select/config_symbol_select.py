"""
- Settings for symbol select.

"""

# TODO: add an inline feature that reads from a file every cycle to add/avoid symbols<>

##############################################################################
#######    Control variables that determine the symbols to trade      ########
#######    -----------------------------------------------------      ########
##############################################################################

##############################################################################
####                                                                      ####
####    STOCK_PRICE_LOW     Stocks will be ABOVE this price               ####
####    STOCK_PRICE_HIGH    Stocks will be BELOW this price               ####
####    ----------------------------------------------------              ####
####    Both are represented in dollars                                   ####
####                                                                      ####
STOCK_PRICE_LOW = 4.00                                                    ####
STOCK_PRICE_HIGH = 7.00                                                   ####
##############################################################################

##############################################################################
####                                                                      ####
####    VOLATILITY_TAIL     Volatility in a certain direction             ####
####    -----------------------------------------------------             ####
####    Options are POSITIVE or NEGATIVE                                  ####
####                                                                      ####
VOLATILITY_TAIL = 'POSITIVE'                                              ####
##############################################################################

##############################################################################
####                                                                      ####
####    VOLATILITY_THRESHOLD    Select volatility above this number       ####
####    -----------------------------------------------------------       ####
####    Represented in dollars                                            ####
####                                                                      ####
VOLATILITY_THRESHOLD = 0.08                                               ####
##############################################################################

##############################################################################
####                                                                      ####
####    VOLATILITY_CUT  CUT isolates based on NUMBER_OF_STOCKS_IN_POOL    ####
####    ------------------------------------------------------            ####
####    Options are TOP, BOTTOM or CENTER                                 ####
####    - TOP       gives the highest volatility                          ####
####    - BOTTOM    gives the lowest volatility                           ####
####    - CENTER    removes top and bottom                                ####
####    CUT happens within the TAIL and THRESHOLD limits                  ####
####                                                                      ####
VOLATILITY_CUT = 'BOTTOM'                                                 ####
##############################################################################

##############################################################################
####                                                                      ####
####    NUMBER_OF_STOCKS_IN_POOL    The number of stocks to start with    ####
####    --------------------------------------------------------------    ####
####    Used during VOLATILITY_CUT process                                ####
####                                                                      ####
NUMBER_OF_STOCKS_IN_POOL = 60                                            ####
##############################################################################

##############################################################################
####                                                                      ####
####    ADD_THESE_STOCKS    Manually add stocks to your list              ####
####    ----------------------------------------------------              ####
####    Injected at the end and NOT counted in NUMBER_OF_STOCKS_IN_POOL   ####
####                                                                      ####
ADD_THESE_STOCKS = []                                                     ####
##############################################################################

##############################################################################
####                                                                      ####
####    AVOID_THESE_STOCKS  Manually remove stocks from your list         ####
####    ----------------------------------------------------              ####
####    Injected at the end and NOT counted in NUMBER_OF_STOCKS_IN_POOL   ####
####                                                                      ####
AVOID_THESE_STOCKS = ['ARDS', 'TUYA', 'ARMP']                             ####
##############################################################################