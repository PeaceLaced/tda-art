# tda-art
Automatic Random Trader for TD Ameritrade

- for educational purposes only/not financial advice

- This is essentially a symbol selection script with trade functionality.


- Using the variables (shown and described below), a list of symbols 
  is generated, and from that list a random symbol is picked and traded.

####################################
####  STOCK SELECT VARIABLES    ####
#### -------------------------- ####
####################################

# only select stocks between these two price points, in dollars
STOCK_PRICE_LOW = 2.00
STOCK_PRICE_HIGH = 5.00

#################################################################
#### PLEASE NOTE:   volatility in this script is simply      ####
####                a change in price between                ####
####                the day before yesterday and yesterday   ####
#################################################################

# POSITIVE or NEGATIVE, VOLATILITY_TAIL is volatility in that direction
VOLATILITY_TAIL = 'POSITIVE'

# VOLATILITY_THRESHOLD gives you volatility that is greater than your number, in dollars
VOLATILITY_THRESHOLD = 0.1

# After tail and threshold, CUT isolates based on POOL
# TOP, BOTTOM or CENTER, top is highest, bottom is lowest, center removes top and bottom
VOLATILITY_CUT = 'BOTTOM'

# how many stocks do you want in the pool to randomly pick from
NUMBER_OF_STOCKS_IN_POOL = 75

# add or remove stocks manually (read as always/never trade)
# calculated AFTER pool is established.
ADD_THESE_STOCKS = []
AVOID_THESE_STOCKS = []

# TODO: add an inline feature that reads from a file every cycle to add/avoid symbols<>

####################################
####  STOCK TRADE VARIABLES     ####
#### -------------------------- ####
####################################        

# these two numbers should stay the same
# how many times do we want to buy and sell a random stock
# trade_cycle means, take position this many times
TRADE_CYCLE_DEFAULT = 300
TRADE_CYCLES = 300   

# how many shares will we buy each round
# TODO: propigate SHARE_QUANTITY to buy/sell checks after KILL_OR_FILL is added <>
SHARE_QUANTITY = 1

# how long should we hold the stock, in seconds
HOLD_STOCK_THIS_LONG = 50

# after selling, how long before we buy again, in seconds
WAIT_BEFORE_BUYING_AGAIN = 10

# stop trying to buy a stock if it fails to fill, in seconds
STOP_TRYING_TO_BUY = 10


##############################################################################################
##########   LONG DESCRIPTION   ##############################################################
##############################################################################################
- STOCK_PRICE_LOW and STOCK_PRICE_HIGH is self explanatory.
- VOLATILITY_TAIL, VOLATILITY_THRESHOLD, VOLATILITY_CUT and NUMBER_OF_STOCKS_IN_POOL
