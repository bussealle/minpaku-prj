# -*- coding: utf-8 -*-
import sys
import json
import plotly
import copy
from original_function import remove_parenthesis,make_touple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

log_name = 'analysis.json'
with open(log_name,'r') as br:
    result = json.load(br)

result['weighted'] = copy.copy(result['tag'])
#result['ids'] = {}

row_n = len(result.keys())%2
col_n = 2
if row_n==0:
    row_n = len(result.keys())//col_n
else:
    row_n = len(result.keys())//col_n+1
fig = plotly.tools.make_subplots(rows=row_n, cols=col_n, subplot_titles=[x for x in result.keys()])
r_c_touple = make_touple(row_n,col_n)
r_c_cnt = 0

plotly.offline.init_notebook_mode(connected=False)
for key in result.keys():
    if key=='weighted':
        for ks in result.keys():
            if ks=='tag' or ks=='weighted':
                continue
            for k in result[ks].keys():
                data = result[ks][k]['data']
                ids = result[ks][k]['id']
                for id in ids:
                    for tag in result['weighted'].keys():
                        if id in result['weighted'][tag]['id']:
                            result['weighted'][tag]['data'] += data
    sorted_res = sorted(result[key].items(), key=lambda x: x[1]['data'], reverse=True)
    names = [x[0] for x in sorted_res]
    values = [x[1]['data'] for x in sorted_res]
    #pred = KMeans(n_clusters=10).fit_predict(values)
    #print(pred)
    sub_fig=plotly.graph_objs.Bar(
        x=names, y=values, name=key,
        #title=log_name,
        #legend={"x":0.8, "y":0.1},
        #yaxis={"title":"Score"},
        )
    # layout = plotly.graph_objs.Layout(
    #     title=log_name,
    #     legend={"x":0.8, "y":0.1},
    #     xaxis={"title":key},
    #     yaxis={"title":"Score"},
    # )
    #sub_fig = plotly.graph_objs.Figure(data=data, layout=layout)
    fig.append_trace(sub_fig, r_c_touple[r_c_cnt][0], r_c_touple[r_c_cnt][1])
    fig['layout']['xaxis'+str(r_c_cnt+1)].update(type='category')
    r_c_cnt += 1

ids = {}
params = []
for key in result.keys():
    if key=='weighted':
        continue
    r = result[key]
    for k in r.keys():
        if k=='null':
            continue
        params.append(key+'_'+k)
        for id in r[k]['id']:
            id_elem = ids.get(id)
            if not id_elem:
                ids[id] = {}
                for ks in result.keys():
                    if ks=='weighted':
                        continue
                    ids[id][ks] = {}
                ids[id][key][k]=r[k]['data']
            else:
                id_elem[key][k]=r[k]['data']
print(params)
print(ids)
id_list = []
id_vec = []
for k1 in ids.keys():
    id_list.append(k1)
    vec = [0] * len(params)
    for k2 in ids[k1].keys():
        for k3 in ids[k1][k2].keys():
            try:
                score = ids[k1][k2][k3]
                vec[params.index(k2+'_'+k3)]=score
            except:
                None
    id_vec.append(vec)

n_clusters = 13
kmeans_model = KMeans(n_clusters=n_clusters, random_state=0, n_jobs=-1)
kmeans_model.fit(id_vec)
labels = kmeans_model.labels_

print(id_vec)
for i in range(n_clusters):
    print('class: '+str(i))
    for j in range(len(labels)):
        if i==labels[j]:
            print(ids[id_list[j]]['tag'].keys())


#fig['layout'].update(height=2000, width=1200, title=log_name)
#plotly.offline.plot(fig)
