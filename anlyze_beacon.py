import json
import sys
import pytz
import pandas as pd
import plotly
from datetime import datetime


with open('log_2018-11-28_08-19-05.json') as f:
    df = json.load(f)

df = df['beacons']
uuids = [len(x['data']) for x in df]
jst = pytz.timezone('Asia/Tokyo')
times = [datetime.fromtimestamp(int(x['time'])).astimezone(jst).strftime('%H:%M:%S') for x in df]

plotly.offline.init_notebook_mode(connected=False)
data = [
    plotly.graph_objs.Scatter(x=times, y=uuids, name="number of uuids")
]

layout = plotly.graph_objs.Layout(
    title="only my environment",
    legend={"x":0.8, "y":0.1},
    xaxis={"title":"Time"},
    yaxis={"title":"UUIDs"},
)

fig = plotly.graph_objs.Figure(data=data, layout=layout)
plotly.offline.plot(fig)
