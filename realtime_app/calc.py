import pymongo
import sys
import json
import pytz
import re
import MeCab
import plotly
import numpy as np
import threading
from datetime import datetime
from make_sparql import spql_get_superconcept,spql_fix_concept
from make_tfidf import normalize,make_tfidf_vector
from make_mecab import parse_on_mecab
from original_func import remove_parenthesis,make_touple
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from gensim.corpora import Dictionary

# Initizlize MongoDB
client = pymongo.MongoClient('localhost',27017)
db = client['minpaku']
#co_full = db['mofull']
co_cat = db['mocat']
co_cache = db['cache']

# JSON Files
beacons_name = 'beacons.json'
with open(beacons_name,'r') as br:
    beacons_js = json.load(br)
jst = pytz.timezone('Asia/Tokyo')
###print(datetime.fromtimestamp(int(logs[10]['time'])).astimezone(jst)-datetime.fromtimestamp(int(logs[9]['time'])).astimezone(jst))

# Dictionary
dict_name = 'dictionary.dct'
dictionary = None
try:
    dictionary = Dictionary.load(dict_name)
except:
    None

# Regex
name_re = r'^(\S+)\s{0,1}(\S+){0,1}＜\S+＞.*$'
name_re = re.compile(name_re)

# Parameters
UUID = "5acf2bbbb7221801b3da001c4d3514ae"
thread_key = ["tag",'country',"region","received",'race',"OCM",'OWC']
CONST_TRANS = 2.3
CONST_ATTEN = 0.5
CONST_SUPER = 0.6


# COSIN SIMILALITY
def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

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
    global dictionary

    result = {}
    combined = []
    completed = []
    super_completed = []

    def proximity_weight(proximity):
        return pow(CONST_ATTEN,proximity)

    def thread_dbpedia(tags):
        nonlocal combined,completed,super_completed
        for tag in tags:
            if (tag['data']==None) or (tag['data'] in completed) or (tag['data'] in super_completed):
                return
            completed.append(tag['data'])
            tag_find = co_cache.find_one({"original_tag" : tag['data']})
            fixed_tag = None
            super_tags = []
            if tag_find:
                fixed_tag = tag_find.get("fixed_tag")
                super_tags = tag_find.get("super_tag")
            else:
                fixed_tag = spql_fix_concept(tag['data'])
                if not '*' in fixed_tag:
                    super_tags = spql_get_superconcept(fixed_tag)
                co_cache.insert({"original_tag" : tag['data'], "fixed_tag" : fixed_tag, "super_tag" : super_tags})
            super_completed += super_tags
            for comb in combined:
                for t in comb:
                    if t['data']==tag['data']:
                        t['data'] = fixed_tag
                        if len(super_tags)>0:
                            for s in super_tags:
                                comb.append({'data':s,'id':t['id']})

    combined = objs
    if sw:
        # for c in combined:
        #     thread_dbpedia(c)
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(thread_dbpedia,combined)
        #combined = new_combined
        #completed = []

    texts = []
    for comb in combined:
        texts.append([x['data'] for x in comb])
    tfidfs,dictionary = make_tfidf_vector(texts, dictionary, super_completed, CONST_SUPER)

    for k,v in tfidfs.items():
        concept = dictionary[k]
        value = v
        ids = []
        for comb in combined:
            for t in comb:
                if t['data']==concept:
                    ids.append(t['id'])

        result[k] = {'data':value*proximity_weight(prox),'id': ids}
    return result

def calc_multiple_score(scores):
    new_score = {}
    if len(scores)==1:
        new_score = scores[0]
    else:
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
                    new_score_tag[tag] = {'data':None,'id':None}
                    new_score_tag[tag]['data'] = score_tag[tag]['data'] #* prox_ratio[i]
                    new_score_tag[tag]['id'] = score_tag[tag]['id']
                    for j in range(i+1,len(scores)):
                        temp = scores[j][key].get(tag)
                        if temp:
                            new_score_tag[tag]['id'] += temp['id']
                            new_score_tag[tag]['data'] += temp['data'] #* prox_ratio[j]
                    visited.append(tag)
    for key in new_score.keys():
        k = list(new_score[key].keys())
        v = normalize([x['data'] for x in list(new_score[key].values())])
        for i in range(len(k)):
            new_score[key][k[i]]['data'] = v[i]
    return new_score

def calc_score(posted_json):
    logs = posted_json
    # Log
    if not type(logs) is list:
        logs = [posted_json]
    # Vars
    all_scores = []
    cnt = 0
    cnt_before = 0
    cnt_all = len(logs)
    cnt_found = 0
    cnt_notfound = 0

    for log in logs:
        # if cnt>10:
        #     continue
        # cnt+=1
        data = log['data']
        time = log['time']
        #time_text = datetime.fromtimestamp(int(time)).astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
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
            vec_radius = [pow(10, (d['txp'][0] - d['rssi'][0]) / (10*CONST_TRANS)) for d in new_ds]

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
                        for i in range(len(tags)):
                            tags[i] = {'data':tags[i], 'id':id}
                        ## print(f"\t|\tid         :\t{obj.get('id')}")
                        ## print(f"\t|\tname       :\t{name[0]}")
                        ## print(f"\t|\ttags       :\t{tags}")
                        ##############
                        if ocm:
                            ocm = ocm.split(', ')
                            for i in range(len(ocm)):
                                ocm[i] = {'data':ocm[i], 'id':id}
                        if owc:
                            owc = owc.split(', ')
                            for i in range(len(owc)):
                                owc[i] = {'data':owc[i], 'id':id}
                        if race:
                            race = race.split('；')[0]
                        if region:
                            match = name_re.match(remove_parenthesis(region))
                            if match:
                                country = match[1]
                                try:
                                    region = match[2]
                                except:
                                    None
                            else:
                                print("region error: "+region)
                        ## print(f"\t|\tcountry    :\t{country}")
                        ## print(f"\t|\tregion     :\t{region}")
                        ## print(f"\t|\trace       :\t{race}")
                        ## print(f"\t|\treceived_in:\t{received}")
                        ## print(f"\timages:\t{imageurls}")
                        ## print("\t|")
                        b_result['tag'].append(tags)
                        if country:
                            b_result['country'].append([{'data':country, 'id':id}])
                        if region:
                            b_result['region'].append([{'data':region, 'id':id}])
                        if race:
                            b_result['race'].append([{'data':race, 'id':id}])
                        if received:
                            b_result['received'].append([{'data':received, 'id':id}])
                        if ocm:
                            b_result['OCM'].append(ocm)
                        if owc:
                            b_result['OWC'].append(owc)

                    ##print("\t【DBPEDIA TAG FIXING】------->")
                    thread_tags = [b_result[x] for x in thread_key]
                    # for q in thread_tags:
                    #     pprint(len(q))
                    # print('------>')
                    thread_prox = [prox] * len(thread_key)
                    thread_sw = [True]*1+[False]*6
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        thread_result = executor.map(calc_single_score,thread_tags,thread_prox,thread_sw)
                        thread_result = list(thread_result)
                    for i in range(len(thread_result)):
                        b_result[thread_key[i]] = thread_result[i]
                    detected_scores.append(b_result)
                    ##pprint("\t【SINGLE ABSTRACTION SCORE】------->")
                    ##pprint(f"\t|\t{b_result}")
                    ##print('\n\n')
            new_score = calc_multiple_score(detected_scores)
            ##print("【MULTIPLE ABSTRACTION SCORE】------->")
            ##print(f"\t{new_score}")
            all_scores.append(new_score)
            ##print(sorted(new_score['tag'].items(), key=lambda x: x[1],reverse=True))
            ##print('--------------------------------------------------------------------------------')
            ##print('\n')
            # percent = cnt/cnt_all*100
            # if (percent-cnt_before) > 1.0:
            #     print(f"{cnt} frame --- {percent}%")
            # cnt_before = percent

    if (not dictionary) or len(all_scores)<1:
        return

    log_calc = None
    log_before = None
    try:
        with open('log_calc.json','r') as f :
            log_calc = json.load(f)
        with open('log_before.json','r') as f :
            log_before = json.load(f)
    except:
        None
    result = log_calc

    if not type(result) is dict:
        result = {}
        for key in thread_key:
            result[key] = {}

    dict_len = len(dictionary.keys())
    vector_exp = []
    weight_env = 1.0
    if len(all_scores)==1 and log_before:
        all_scores.insert(0,log_before)
    for s in all_scores:
        vec = np.zeros(dict_len)
        for key in s.keys():
            for k,v in s[key].items():
                vec[int(k)] += v['data']
        vector_exp.append(vec)
    if len(vector_exp)>1:
        weight_env = cos_sim(v1=vector_exp[0],v2=vector_exp[1])
        pprint(weight_env)
    log_before = all_scores[-1]

    for s in all_scores[1:]:
        for key in s.keys():
            for k in s[key].keys():
                find = result[key].get(str(k))
                if find:
                    result[key][str(k)]['data'] += s[key][k]['data']*weight_env
                    for i in s[key][k]['id']:
                        if not i in result[key][str(k)]['id']:
                            result[key][str(k)]['id'].append(i)
                else:
                    result[key][str(k)] = {'data':None,'id':None}
                    result[key][str(k)]['data'] = s[key][k]['data']*weight_env
                    result[key][str(k)]['id'] = s[key][k]['id']

    dictionary.save(dict_name)
    with open('log_calc.json','w') as of:
            json.dump(result,of,indent=4)
    with open('log_before.json','w') as of:
            json.dump(log_before,of)

if __name__=='__main__':
    l = [{
        "data": {
        "88f4bfffde6d0e02011a0aff4c001005": [
            {
                "major": 284,
                "uuid": "88f4bfffde6d0e02011a0aff4c001005",
                "mac": "6d:de:ff:bf:f4:88",
                "time": "1542676534",
                "rssi": [
                    -32
                ],
                "minor": 45965,
                "txp": [
                    32
                ]
            },
            {
                "major": 284,
                "uuid": "88f4bfffde6d0e02011a0aff4c001005",
                "mac": "6d:de:ff:bf:f4:88",
                "time": "1542676535",
                "rssi": [
                    -25
                ],
                "minor": 45965,
                "txp": [
                    32
                ]
            }
        ],
        "010001e367035d957c0b02010607ff4c": [
            {
                "major": 16,
                "uuid": "010001e367035d957c0b02010607ff4c",
                "mac": "7c:95:5d:03:67:e3",
                "time": "1542676534",
                "rssi": [
                    -46
                ],
                "minor": 523,
                "txp": [
                    0
                ]
            },
            {
                "major": 16,
                "uuid": "010001e367035d957c0b02010607ff4c",
                "mac": "7c:95:5d:03:67:e3",
                "time": "1542676534",
                "rssi": [
                    -60
                ],
                "minor": 523,
                "txp": [
                    0
                ]
            },
            {
                "major": 16,
                "uuid": "010001e367035d957c0b02010607ff4c",
                "mac": "7c:95:5d:03:67:e3",
                "time": "1542676535",
                "rssi": [
                    -66
                ],
                "minor": 523,
                "txp": [
                    0
                ]
            },
            {
                "major": 16,
                "uuid": "010001e367035d957c0b02010607ff4c",
                "mac": "7c:95:5d:03:67:e3",
                "time": "1542676535",
                "rssi": [
                    -61
                ],
                "minor": 523,
                "txp": [
                    0
                ]
            }
        ],
        "5acf2bbbb7221801b3da001c4d3514ae": [
            {
                "major": 101,
                "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
                "mac": "c0:1c:4d:44:47:f9",
                "time": "1542676534",
                "rssi": [
                    -97
                ],
                "minor": 6,
                "txp": [
                    -89
                ]
            },
            {
                "major": 101,
                "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
                "mac": "c0:1c:4d:45:42:e5",
                "time": "1542677339",
                "rssi": [
                -81
                ],
                "minor": 9,
                "txp": [
                -93
                ]
            },
            {
                "major": 101,
                "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
                "mac": "c0:1c:4d:45:42:e5",
                "time": "1542677339",
                "rssi": [
                -81
                ],
                "minor": 9,
                "txp": [
                -93
                ]
            }
        ],
        "fa4360caa1430e02011a0aff4c001005": [
            {
                "major": 796,
                "uuid": "fa4360caa1430e02011a0aff4c001005",
                "mac": "43:a1:ca:60:43:fa",
                "time": "1542676534",
                "rssi": [
                    -91
                ],
                "minor": 4454,
                "txp": [
                    124
                ]
            }
        ],
        "9dd893ec327b0e02011a0aff4c001005": [
            {
                "major": 2588,
                "uuid": "9dd893ec327b0e02011a0aff4c001005",
                "mac": "7b:32:ec:93:d8:9d",
                "time": "1542676534",
                "rssi": [
                    -60
                ],
                "minor": 48524,
                "txp": [
                    49
                ]
            },
            {
                "major": 2588,
                "uuid": "9dd893ec327b0e02011a0aff4c001005",
                "mac": "7b:32:ec:93:d8:9d",
                "time": "1542676535",
                "rssi": [
                    -61
                ],
                "minor": 48524,
                "txp": [
                    49
                ]
            }
        ]
        },
        "time": "1542676535"
    }]
    calc_score(l)
