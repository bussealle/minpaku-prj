import pymongo
import sys
import json
import pytz
from datetime import datetime
from sparql_test import get_dbpedia
from mecab_test import parse_on_mecab
import re
import MeCab
import plotly
from original_function import remove_parenthesis,make_touple

# SEARCH ON MONGODB
def search_on_mongo(beacon_num,beacons_js):
    b_num = str(beacon_num)
    beacon = beacons_js.get(b_num)
    result = []
    if not beacon:
        return result
    ids = beacon['ids']
    for target_id in ids:
        obj = co_cat.find_one({"id" : target_id})
        if obj:
            result.append(obj)
    return result

# CALCULATE RELATIVE SCORE
def calc_single_score(objs,prox,sw=True):

    def proximity_weight(proximity):
        weight = 1.0 #0.0~1.0
        return 1/(proximity*weight)

    result = {}
    combined = []
    completed = []
    for obj in objs:
        if not obj:
            continue
        if type(obj)!=list:
            obj = [obj]
        combined = combined + obj
    total = len(combined)
    if sw:
        new_combined = []
        for tag in combined:
            if not tag in completed:
                tag_temp = 'dbpj:' + tag
                fixed_tags = get_dbpedia(sub=tag_temp,pre='dbp-owl:wikiPageRedirects',obj='?val')
                if fixed_tags:
                    new_tag = fixed_tags[0]['val']['value'].split('/')[-1]
                    ##print("\t|\t"+tag+' → '+new_tag+f"  ({fixed_tags[0]['val']['value']})")
                    completed.append(tag)
                    for t in combined:
                        if t==tag:
                            new_combined.append(new_tag)
                else:
                    found_dbpedia = get_dbpedia(sub=tag_temp,pre='dbpedia-owl:wikiPageID',obj='?re')
                    if not found_dbpedia:
                        tag = tag+'*'
                    new_combined.append(tag)
        combined = new_combined
        completed = []
    for r in combined:
        if r in completed:
            continue
        result[r] = combined.count(r)/total*proximity_weight(prox)
        completed.append(r)
    return result

def calc_multiple_score(scores,proximity):

    if len(scores)==1:
        return scores[0]
    prox_sum = sum([x for x in proximity])
    prox_ratio = [1/(x/prox_sum) for x in proximity]
    prox_sum = sum(prox_ratio)
    prox_ratio = [x/prox_sum for x in prox_ratio]
    ###print(proximity)
    ###print(prox_ratio)
    new_score = {}
    for key in scores[0].keys():
        new_score[key] = {}
    for key in new_score.keys():
        visited = []
        for i in range(len(scores)):
            score = scores[i]
            if not score:
                continue
            score_tag = score[key]
            new_score_tag = new_score[key]
            for tag in score_tag.keys():
                if tag in visited:
                    continue
                new_score_tag[tag] = score_tag[tag] * prox_ratio[i]
                for j in range(i+1,len(scores)):
                    temp = scores[j][key].get(tag)
                    if temp:
                        new_score_tag[tag] += temp * prox_ratio[j]
                visited.append(tag)
    return new_score

# Initizlize MongoDB
client = pymongo.MongoClient('localhost',27017)
db = client['minpaku']
co_full = db['mofull']
co_cat = db['mocat']

# JSON Files
beacons_name = 'beacons.json'
log_name = 'log_2018-11-20_10-15-30.json'
with open(beacons_name,'r') as br:
    beacons_js = json.load(br)
with open(log_name) as f :
    logs = json.load(f)['beacons']
jst = pytz.timezone('Asia/Tokyo')
###print(datetime.fromtimestamp(int(logs[10]['time'])).astimezone(jst)-datetime.fromtimestamp(int(logs[9]['time'])).astimezone(jst))

# Regex
name_re = r'^(\S+)\s{0,1}(\S+){0,1}＜\S+＞.*$'
name_re = re.compile(name_re)

# Parameters
cnt_found = 0
cnt_notfound = 0
UUID = "5acf2bbbb7221801b3da001c4d3514ae"

# Vars
all_scores = []
cnt = 0
cnt_before = 0
cnt_all = len(logs)

for log in logs:
    if cnt>10:
        continue
    cnt+=1
    data = log['data']
    time = log['time']
    time_text = datetime.fromtimestamp(int(time)).astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
    ds = data.get(UUID)
    if ds :
        new_ds = []
        for i in range(len(ds)):
            d = ds[i]
            minor = d['minor']
            if minor in [x['minor'] for x in new_ds]:
                continue
            temp = [x for x in ds if x['minor']==minor]
            new_rssi = sum([x['rssi'][0] for x in temp])/len(temp)
            new_txp = sum([x['txp'][0] for x in temp])/len(temp)
            d['rssi'][0] = new_rssi
            d['txp'][0] = new_txp
            new_ds.append(d)
        vec_rssi = [d['rssi'][0] for d in new_ds]
        vec_txp = [d['txp'][0] for d in new_ds]
        vec_minor = [d['minor'] for d in new_ds]
        vec_radius = [pow(10, (d['txp'][0] - d['rssi'][0]) / 20) for d in new_ds]

        # if cnt!=0:
        #     continue
        # if len(vec_minor)==1 and vec_minor[0]==1:
        #     cnt+=1
        # if (len(vec_minor)==4):
        #     cnt+=1
        # else:
        #     continue

        ##print('')
        ##print(f"{time_text}----------------------------------------------------------------------")
        ##print("【DETECTED BEACONS】")
        detected_scores = []
        for i in range(len(vec_minor)):
            ##print(f"\tMinor:\t{vec_minor[i]}")
            ##print(f"\t|\tRSSI     \t:\t{vec_rssi[i]}")
            ##print(f"\t|\tTxPower  \t:\t{vec_txp[i]}")
            ##print(f"\t|\tProximity\t:\t{vec_radius[i]}")
            ##############
            prox = vec_radius[i]
            b_result = {"tag":[],"country":[],"region":[],"received":[],"race":[],"OCM":[],"OWC":[]}
            objs = search_on_mongo(beacon_num=vec_minor[i],beacons_js=beacons_js)
            if len(objs)==0:
                detected_scores.append(None)
            else:
                ##print("\t|")
                ##print("\t【EXHIBIT INFOMATION】------->")
                for obj in objs:
                    id = obj.get('id')
                    imageurls = obj.get('imageurls')
                    name = obj.get('name')
                    region = obj.get('region')
                    race = obj.get('race')
                    received = obj.get('received_in')
                    ocm = obj.get('OCM')
                    owc = obj.get('OWC')
                    country = None
                    name = name.split('\n')
                    tags = parse_on_mecab(name[0])
                    for t in tags:
                        t = {'data':t, 'id':id}
                    ##print(f"\t|\tid         :\t{obj.get('id')}")
                    ##print(f"\t|\tname       :\t{name[0]}")
                    ##print(f"\t|\ttags       :\t{tags}")
                    ##############
                    if ocm:
                        ocm = ocm.split(', ')
                    if race:
                        race = race.split('；')[0]
                    match = name_re.match(remove_parenthesis(region))
                    if match:
                        country = match[1]
                        try:
                            region = match[2]
                        except:
                            None
                    else:
                        print("region error: "+region)
                    ##print(f"\t|\tcountry    :\t{country}")
                    ##print(f"\t|\tregion     :\t{region}")
                    ##print(f"\t|\trace       :\t{race}")
                    ##print(f"\t|\treceived_in:\t{received}")
                    ###print(f"\timages:\t{imageurls}")
                    ##print("\t|")
                    b_result['tag'].append(tags)
                    b_result['country'].append({'data':country, 'id':id})
                    b_result['region'].append({'data':region, 'id':id})
                    b_result['race'].append({'data':race, 'id':id})
                    b_result['received'].append({'data':received, 'id':id})
                    b_result['OCM'].append({'data':ocm, 'id':id})
                    b_result['OWC'].append({'data':owc, 'id':id})
                ##print("\t【DBPEDIA TAG FIXING】------->")
                b_result["tag"] = calc_single_score(b_result['tag'],prox)
                b_result['country'] = calc_single_score(b_result['country'],prox)
                b_result["region"] = calc_single_score(b_result['region'],prox)
                b_result["received"] = calc_single_score(b_result['received'],prox,sw=False)
                b_result['race'] = calc_single_score(b_result['race'],prox,sw=False)
                b_result["OCM"] = calc_single_score(b_result['OCM'],prox,sw=False)
                b_result['OWC'] = calc_single_score(b_result['OWC'],prox,sw=False)
                detected_scores.append(b_result)
                ##print("\t【SINGLE ABSTRACTION SCORE】------->")
                ##print(f"\t|\t{b_result}")
                ##print('\n\n')
        new_score = calc_multiple_score(detected_scores,vec_radius)
        ##print("【MULTIPLE ABSTRACTION SCORE】------->")
        ##print(f"\t{new_score}")
        all_scores.append(new_score)
        ##print(sorted(new_score['tag'].items(), key=lambda x: x[1],reverse=True))
        ##print('--------------------------------------------------------------------------------')
        ##print('\n')
        percent = cnt/cnt_all*100
        if (percent-cnt_before) > 1.0:
            print(f"{cnt} frame --- {percent}%")
        cnt_before = percent


result = {}
for key in all_scores[0].keys():
    result[key] = {}
for s in all_scores:
    for key in s.keys():
        for k in s[key].keys():
            find = result[key].get(k)
            if find:
                result[key][k] += s[key][k]
            else:
                result[key][k] = s[key][k]

tag_find_cnt = 0
for key in result['tag'].keys():
    if key.find('*')!=-1:
        remove_parenthesis(region)
        tag_find_cnt += 1

print(f"\t\tDBpedia connected ratio\t:\t{100-tag_find_cnt/len(result['tag'].keys())*100} %")
row_n = len(result.keys())%2
col_n = 2
if row_n==0:
    row_n = len(result.keys())//col_n
else:
    row_n = len(result.keys())//col_n+1
fig = plotly.tools.make_subplots(rows=row_n, cols=col_n, subplot_titles=[x for x in result.keys()])
r_c_touple = make_touple(row_n,col_n)
r_c_cnt = 0

for key in result.keys():
    sorted_res = sorted(result[key].items(), key=lambda x: x[1],reverse=True)
    names = [x[0] for x in sorted_res]
    values = [x[1] for x in sorted_res]
    plotly.offline.init_notebook_mode(connected=False)
    sub_fig=plotly.graph_objs.Bar(
        x=names, y=values, name=key, #title=log_name,
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

fig['layout'].update(height=2000, width=1200, title=log_name)
plotly.offline.plot(fig)
###print("{0}%".format(cnt_found/(cnt_found+cnt_notfound)*100))
