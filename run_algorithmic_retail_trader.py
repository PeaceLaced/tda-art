#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat 27 Nov 03:42:45 2021

- NOTICE:
    - for educational purposes only
    - not financial advice

- SUPPORT:
    - https://www.twitch.tv/peacelaced
    - https://www.patreon.com/peacelaced
    - Donate Crypto:
        - WAX: rd2wo.wam
        - CoinBase: @peacelaced
        - MetaMask: 0x567ec43065991e4269Be19F4aEcac8C93c587619
    
@author: Brandon Black (PeaceLaced)
@source: https://github.com/PeaceLaced/tda-art
"""

import sys
import asyncio



opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

if "-chart" in opts:
    
    # for now this runs a dash chart, future, crate more opts
    import z_art.data_visual.app
    
else:
    from z_art.progress_report.api_progress_report import Progress as progress
    progress.w('IDENTIFY_SCRIPT_(run_algorithmic_retail_trader.py)')
    from z_art.__main__ import cli_main
    asyncio.run(cli_main())