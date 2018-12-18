import sys
import json
import re

beacons_name = 'beacons.json'
exhibition_list = 'exhibition.txt'
regexp = r'^[A-Z]{1}[0-9]{7}'

with open(beacons_name,'r') as br:
    beacons = json.load(br)
    f = open(exhibition_list,'r')
    line = f.readline()
    beacon_num = '0'
    while line:
        match = re.match(r'[0-9]+',line)
        if match:
            beacon_num = match[0]
            ids = beacons[beacon_num]['ids']
            if not type(ids) is list:
                ids = []
        else:
            match = re.match(regexp,line)
            if match:
                try:
                    newid = match[0]
                    ids = beacons[beacon_num]['ids']
                    if not newid in ids:
                        print('inserted: ' + newid)
                        ids.append(newid)
                    else:
                        print('skipped: ' + newid)
                except:
                    print('err')
            else:
                print(beacon_num + ": " + line)
        line = f.readline()
    f.close()
    with open(beacons_name,'w') as bw:
        json.dump(beacons,bw,indent=4)
