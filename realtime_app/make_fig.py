import numpy as np
import pandas as pd
import plotly
import json
import copy
from original_func import remove_parenthesis,make_touple
from gensim.corpora import Dictionary


dict_name = 'dictionary.dct'

def make_fig(log_name):
    dictionary = None
    try:
        dictionary = Dictionary.load(dict_name)
    except:
        None
    result = None
    try:
        with open(log_name,'r') as br:
            result = json.load(br)
    except:
        return result

    result['weighted'] = copy.copy(result['tag'])

    row_n = len(result.keys())%2
    col_n = 2
    if row_n==0:
        row_n = len(result.keys())//col_n
    else:
        row_n = len(result.keys())//col_n+1
    fig = plotly.tools.make_subplots(rows=row_n, cols=col_n, subplot_titles=[x for x in result.keys()], print_grid=False)
    r_c_touple = make_touple(row_n,col_n)
    r_c_cnt = 0

    #plotly.offline.init_notebook_mode(connected=False)
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
        names = [dictionary[int(x[0])] for x in sorted_res]
        values = [x[1]['data'] for x in sorted_res]
        sub_fig=plotly.graph_objs.Bar(
            x=names, y=values, name=key,
            )
        fig.append_trace(sub_fig, r_c_touple[r_c_cnt][0], r_c_touple[r_c_cnt][1])
        fig['layout']['xaxis'+str(r_c_cnt+1)].update(type='category')
        r_c_cnt += 1
    fig['layout'].update(height=2000, width=1200, title=log_name)
    return fig
