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

from z_art.progress_report.config_progress_report import Progress as progress

progress.w('IDENTIFY_SCRIPT_(run_automatic_random_trader.py)')

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

if "-gui" in opts:
    
    # import gui app (does NOT exist)
    from z_art.app_gui import gui_main
    
    # call the main gui function (does NOT exist)
    gui_main()
    
else:
    
    # import the main cli function from __main__
    from z_art.__main__ import cli_main
    
    # call the main function with asyncio capability
    asyncio.run(cli_main())