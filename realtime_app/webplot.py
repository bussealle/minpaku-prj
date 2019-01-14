# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from make_fig import make_fig
import pytz
import base64


# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

jst = pytz.timezone('Asia/Tokyo')

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.Div([
        html.H4('みんぱくモニタ'),
        html.Div(id='live-update-text'),
        #html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
        html.Img(id='live-update-image'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=3 * 1000  # in milliseconds
        )
    ])
],
    #style={'backgroundColor': colors['background'], 'color': colors['text']}
)

@app.callback(Output('live-update-text', 'children'),
              events=[Event('interval-component', 'interval')])
def update_metrics():
    now = datetime.now()
    time = now.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('datetime: {}'.format(time), style=style),
    ]

@app.callback(Output('live-update-graph', 'figure'),
              events=[Event('interval-component', 'interval')])
def update_graph_live():
    fig = make_fig('log_calc.json')
    return fig

@app.callback(Output('live-update-image', 'src'),
              events=[Event('interval-component', 'interval')])
def update_image_live():
    image_filename = 'map.png' # replace with your own image
    src = None
    try:
        encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode()
        src='data:image/png;base64,{}'.format(encoded_image)
    except:
        None
    return src

if __name__ == '__main__':
    app.run_server(host="127.0.0.1", port=5000, debug=True)
