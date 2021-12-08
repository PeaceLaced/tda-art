# tda-art

Automatic Random Trader for TD Ameritrade (current version)

Automatic Retail Trader for TD Ameritrade (future version)

- requirements: TDA-API, loguru, tqdm

- for educational purposes only/not financial advice

- This is essentially a symbol selection script with trade functionality.

- This may NOT work on the cloud (Nasdaq sometimes blocks access)
  - This should always work locally, but be aware each run pulls from Nasdaq.

- This script does NOT use or need a database.
  - This script logs to a few different files, but can easily be converted to DB if you like.

- This script trades using TDA-API's equity_buy_market() and equity_sell_market() methods.
  - These two methods are intended for LONG non LIMIT orders.
  - If you want LIMIT or SHORT, make the changes, but be warned, I have NOT used it in this way.

- This script currently only works during normal market hours. 
  - It is easy to add pre and post market functionality, but I have no interest in trading those hours, so I will not add it.
  - SEE: https://tda-api.readthedocs.io/en/latest/order-builder.html#order-builder
  - SEE: https://tda-api.readthedocs.io/en/latest/order-builder.html#tda.orders.common.Session

- Using the variables (shown and described below), a list of symbols is generated, and from that list a random symbol is picked and traded.

- The word volatility in this script is simply a change in price between the day before yesterday and yesterday
  - This is obtained from the Nasdaq Screener under Net Change for each symbol.
  - All values extracted from the Nasdaq Screener are typically from the previous day, unless they update their screener mid day.

- The variables below are located at around line 240, and are as follows:

- STOCK_PRICE_LOW is the lowest price to filter
- STOCK_PRICE_HIGH is the highest price to filter
  - You will always trade stocks between these two prices (relative to what the Nasdaq Screener places in the 'lastsale' field)

- VOLATILITY_TAIL can be POSITIVE or NEGATIVE
  - positive is a change between day before yesterday and yesterday in the positive direction (Nasdaq Screener 'netchange' field)
  - negative is a change between day before yesterday and yesterday in the negative direction (Nasdaq Screener 'netchange' field)
  - I have only ever used POSITIVE. 

- VOLATILITY_THRESHOLD is the amount of change.
  - if TAIL is positive, it will select stocks that are greater than THRESHOLD in the positive direction
  - if TAIL is negative, it will select stocks that are grater than THRESHOLD in the negative direction

- VOLATILITY_CUT works within the TAIL after THRESHOLD
  - options here are TOP, BOTTOM and CENTER
  - this is used in conjunction with POOL
  - top will give you the stocks that changed the most
  - bottom will give you the stocks that changed the least
  - center cuts the top and bottom, and gives you the center. 
  - center typically skews toward bottom because high change in price is more rare

- NUMBER_OF_STOCKS_IN_POOL can be set to any number. I typically play around with between 25 and 75.
  - pool is directly related to cut in that it gives you the amount toward the cut you select.

- ADD_THESE_STOCKS allow you to put symbols into the list
- AVOID_THESE_STOCKS will remove the stock if it happens to be selected
  - add and avoid happen after the pool is made, so it counts toward or against the pool.
  - example, 75 in pool, two add, one avoid, means 76 instead of 75
  - example, 50 in pool, four add, seven avoid, 47 instead of 50

- TODO: I plan to add an inline feature that will read from a file to add and avoid while the script is running

- TRADE_CYCLE_DEFAULT and TRADE_CYCLES are exactly the same and should always be the same value
  - default is used to show how many total cycles are going to happen (reported every cycle)
  - cycles is used to show what cycle you are on (also reported every cycle)

- SHARE_QUANTITY is how many shares you want to buy and sell for the randomly selected symbol
  - ***CAUTION*** the script currently only supports 1 share.
  - a future release will allow for multiple shares and take advantage of fill_or_kill on the buy

- HOLD_STOCK_THIS_LONG is how long we hold the stock before selling. It is represented in seconds.
  - I build this script to scalp, and have never set this to higher than 50 seconds.

- WAIT_BEFORE_BUYING_AGAIN is how long to pause after the last stock sold, before buying again, represented in seconds
  - this in conjunction with hold_stock_this_long gives us one cycle, and roughtly equals the two added together (increases during fill waits)

- STOP_TRYING_TO_BUY is the how many seconds to wait before a fail to fill cancels the order
  - my default has always been 10, but it never hits that mark. 
  - under the hood, every one second it asks tda about the order status, and after STOP_TRYING_TO_BUY is reached, it will cancel
  - this setting may go away once functionality for more shares is added and fill_or_kill is used
  - NOTE that this only pertains to the buy order. The sell order will cycle indefinetly until the order is filled.
