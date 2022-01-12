# -*- coding: utf-8 -*-
'''
https://github.com/theo-brown/dash-examples/blob/7dbd25c758b370dbbbae454cb147d64ea0ea2d95/basic-realtime-plot.py
'''
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
from time import time
from datetime import datetime, timedelta, date
import pytz
from z_art.progress_report.api_progress_report import Progress as progress
from random import randrange, uniform
'''
Default template: 'plotly'
Available templates: ['ggplot2', 'seaborn', 'simple_white', 'plotly',
                      'plotly_white', 'plotly_dark', 'presentation', 
                      'xgridoff', 'ygridoff', 'gridon', 'none']
'''
import plotly.io as pio
pio.templates.default = "plotly_dark"

REFRESH_RATE_MS = 30000

start_time = time()
since_start = time() - start_time
generated_date = date.today().strftime('%d-%b-%Y')
test_data = []
acc_profits = 0

def generate_data():
    
    # PROFIT_dd-mmm-yyyy.log (dd-mmm-yyyy)
    # testing with PROFIT_07-Jan-2022.log
    manually_set_file_date = False
    
    if not manually_set_file_date:
        file_name = 'z_art/data_visual/data_dump/PROFIT_' + generated_date + '.log'
        
    if manually_set_file_date:
        file_name = 'z_art/data_visual/data_dump/PROFIT_' + manually_set_file_date + '.log'
    '''    
    # WRITE DATA TO FILE
    
    random_profit = round(uniform(-0.99, 0.99), 2)
    test_data.append(('SYM', str(random_profit)))
    
    # we want to write the accumulation, not the individual
    
    for profit_tuple in test_data:
        acc_profits = profit_tuple[1]
        f = open(file_name, 'w+')
        f.write(str(acc_profits))
        f.close()
    '''    
    # READ DATA FROM FILE

    f = open(file_name, 'r')
    read_file_data = f.readline()
    f.close()
    
    return datetime.now(pytz.timezone('US/Eastern')) - timedelta(since_start), read_file_data

app = dash.Dash(__name__, update_title=None)

#figure_margin = go.layout.Margin(b=0, l=0, r=0, t=0) 

fig = go.Figure(go.Scatter(x=[], y=[], mode='lines'), 
                layout={'xaxis_title': "Time (s)",
                        'yaxis_title': "X",
                        'font_family': 'Nunito, sans-serif',
                        'font_size': 12,
                        #'margin': figure_margin
                        'margin_b':25,
                        'margin_l':25,
                        'margin_r':25,
                        'margin_t':25})

live_update_graph_1 = dcc.Graph(id='live_update_graph_1',
                                animate=False,
                                style={'width': '100%'},
                                config={'displayModeBar': False,
                                        'staticPlot': True},
                                figure=fig)

app.layout = html.Div([
                 html.Div([
                     html.H2("Realized Profit/Loss"),
                     live_update_graph_1, # dcc.Graph()
                     dcc.Interval(id='update_timer_1', interval=REFRESH_RATE_MS)])])
    
# when input is changed, output changes automatically
                    # component_id, component_property
@app.callback(Output('live_update_graph_1', 'extendData'),
              Input('update_timer_1', 'n_intervals'))

# automatically called when then input changes
def update_graph_1(n_intervals: int):

    new_x, new_y = generate_data()
    # when False is passed to new_x/y, nothing should happen
    if new_x:
        if new_y:
            return {'x': [[new_x]],
                    'y': [[new_y]]}, [0], None
    # because extendData is the component_property of output
    # new_x and new_y are appended to the trace at component_id live_update_graph_1

app.run_server(debug=True, use_reloader=False, dev_tools_ui=False)