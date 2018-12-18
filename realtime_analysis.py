from flask import Flask,request,jsonify,make_response,abort

app = Flask(__name__)

@app.route("/data", methods=['GET'])
def getData():
    params = request.args
    response = {}
    if 'param' in params:
        response.setdefault('res', 'param is : ' + params.get('param'))
    return make_response(jsonify(response))

@app.route("/data",methods=['POST'])
def postData():
    params = request.json
    if not params:
        return abort(404)
    response = {}
    if 'data' in params and 'time' in params:
        response.setdefault('res', 'data found')
    else:
        return abort(404)
    return make_response(jsonify(response))


app.run(host="127.0.0.1", port=5000)
