import requests
import json
import time

log_name = 'log_2018-12-21_16-31-40.json'
with open(log_name) as f :
     logs = json.load(f)['beacons']
# logs = [{
#     "data": {
#     "88f4bfffde6d0e02011a0aff4c001005": [
#         {
#             "major": 284,
#             "uuid": "88f4bfffde6d0e02011a0aff4c001005",
#             "mac": "6d:de:ff:bf:f4:88",
#             "time": "1542676534",
#             "rssi": [
#                 -32
#             ],
#             "minor": 45965,
#             "txp": [
#                 32
#             ]
#         },
#         {
#             "major": 284,
#             "uuid": "88f4bfffde6d0e02011a0aff4c001005",
#             "mac": "6d:de:ff:bf:f4:88",
#             "time": "1542676535",
#             "rssi": [
#                 -25
#             ],
#             "minor": 45965,
#             "txp": [
#                 32
#             ]
#         }
#     ],
#     "010001e367035d957c0b02010607ff4c": [
#         {
#             "major": 16,
#             "uuid": "010001e367035d957c0b02010607ff4c",
#             "mac": "7c:95:5d:03:67:e3",
#             "time": "1542676534",
#             "rssi": [
#                 -46
#             ],
#             "minor": 523,
#             "txp": [
#                 0
#             ]
#         },
#         {
#             "major": 16,
#             "uuid": "010001e367035d957c0b02010607ff4c",
#             "mac": "7c:95:5d:03:67:e3",
#             "time": "1542676534",
#             "rssi": [
#                 -60
#             ],
#             "minor": 523,
#             "txp": [
#                 0
#             ]
#         },
#         {
#             "major": 16,
#             "uuid": "010001e367035d957c0b02010607ff4c",
#             "mac": "7c:95:5d:03:67:e3",
#             "time": "1542676535",
#             "rssi": [
#                 -66
#             ],
#             "minor": 523,
#             "txp": [
#                 0
#             ]
#         },
#         {
#             "major": 16,
#             "uuid": "010001e367035d957c0b02010607ff4c",
#             "mac": "7c:95:5d:03:67:e3",
#             "time": "1542676535",
#             "rssi": [
#                 -61
#             ],
#             "minor": 523,
#             "txp": [
#                 0
#             ]
#         }
#     ],
#     "5acf2bbbb7221801b3da001c4d3514ae": [
#         {
#             "major": 101,
#             "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
#             "mac": "c0:1c:4d:44:47:f9",
#             "time": "1542676534",
#             "rssi": [
#                 -97
#             ],
#             "minor": 6,
#             "txp": [
#                 -89
#             ]
#         },
#         {
#             "major": 101,
#             "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
#             "mac": "c0:1c:4d:45:42:e5",
#             "time": "1542677339",
#             "rssi": [
#             -81
#             ],
#             "minor": 9,
#             "txp": [
#             -93
#             ]
#         },
#         {
#             "major": 101,
#             "uuid": "5acf2bbbb7221801b3da001c4d3514ae",
#             "mac": "c0:1c:4d:45:42:e5",
#             "time": "1542677339",
#             "rssi": [
#             -81
#             ],
#             "minor": 9,
#             "txp": [
#             -93
#             ]
#         }
#     ],
#     "fa4360caa1430e02011a0aff4c001005": [
#         {
#             "major": 796,
#             "uuid": "fa4360caa1430e02011a0aff4c001005",
#             "mac": "43:a1:ca:60:43:fa",
#             "time": "1542676534",
#             "rssi": [
#                 -91
#             ],
#             "minor": 4454,
#             "txp": [
#                 124
#             ]
#         }
#     ],
#     "9dd893ec327b0e02011a0aff4c001005": [
#         {
#             "major": 2588,
#             "uuid": "9dd893ec327b0e02011a0aff4c001005",
#             "mac": "7b:32:ec:93:d8:9d",
#             "time": "1542676534",
#             "rssi": [
#                 -60
#             ],
#             "minor": 48524,
#             "txp": [
#                 49
#             ]
#         },
#         {
#             "major": 2588,
#             "uuid": "9dd893ec327b0e02011a0aff4c001005",
#             "mac": "7b:32:ec:93:d8:9d",
#             "time": "1542676535",
#             "rssi": [
#                 -61
#             ],
#             "minor": 48524,
#             "txp": [
#                 49
#             ]
#         }
#     ]
#     },
#     "time": "1542676535"
# }]

url = "http://127.0.0.1:5001/data"
headers = {'content-type': 'application/json'}
cnt = 1
print("all: "+str(len(logs)))
for log in logs:
    if cnt%10==0:
        print(cnt)
    response = requests.post(url, data=json.dumps(log), headers=headers)
    time.sleep(3)
    cnt+=1
print("completed: "+str(cnt))
