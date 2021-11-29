#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 03:42:45 2021

- run this file to launch the application

- REQUIREMENTS:
    - tda-api
    - loguru
    - tqdm

@author: brandon (PeaceLaced)
"""

import sys
import asyncio

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

if "-gui" in opts:
    
    # for future use, this file does not currently exist
    from z_automatic_random_trader.app_gui import gui_main
    
    gui_main()
    
else:
    
    from z_automatic_random_trader.__main__ import cli_main
    
    asyncio.run(cli_main())
    #cli_main()