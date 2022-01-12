## Algorithmic Retail Trader for TD Ameritrade
<details><summary>SOURCE</summary>
<p>

- https://github.com/PeaceLaced/tda-art
</p></details>

<details><summary>NOTICE</summary>
<p>

- for educational purposes only
- not financial advice
</p></details>

<details><summary>AUTHOR</summary>
<p>

- Brandon Black (PeaceLaced)
</p></details>

<details><summary>SUPPORT ME</summary>
<p>

- https://www.twitch.tv/peacelaced
- https://www.patreon.com/peacelaced
- Donate Crypto:
    - WAX: rd2wo.wam
    - CoinBase: @peacelaced
    - MetaMask: 0x567ec43065991e4269Be19F4aEcac8C93c587619
</p></details>

### Follow these steps to start trading.
1) **authenticate application**
   - create a TD Ameritrade [developer account](https://developer.tdameritrade.com/)
   - put those settings in the [config file](https://github.com/PeaceLaced/tda-art/blob/main/z_art/td_ameritrade/config_td_ameritrade.py)
   - authenticate using [tda-api](https://github.com/alexgolec/tda-api)
       - for help with this, visit [tda-api discord](https://discord.gg/BEr6y6Xqyv)
2) **configure the application**
   - set the [strategy](https://github.com/PeaceLaced/tda-art/blob/main/z_art/__main__.py)
   - configure strategy constants
       - RANDOM [strategy settings](https://github.com/PeaceLaced/tda-art/blob/main/z_art/strategy_select/strat_random/main_strat_random.py)
       - TRIPPLEWIN [strategy settings](https://github.com/PeaceLaced/tda-art/blob/main/z_art/strategy_select/strat_tripplewin/main_strat_tripplewin.py)
       - BASELINE (or use this template to build your own strategy)
   - set [symbol select params](https://github.com/PeaceLaced/tda-art/blob/main/z_art/symbol_select/main_symbol_select.py)
3) **start the** [run script](https://github.com/PeaceLaced/tda-art/blob/main/run_algorithmic_retail_trader.py) **from the CLI**
