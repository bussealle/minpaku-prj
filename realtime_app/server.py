from flask import Flask,request,jsonify,make_response,abort
import make_map
import calc

dictionary = None
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
    global before
    params = request.json
    if not params:
        return abort(404)
    response = {}
    if 'data' in params and 'time' in params:
        calc.calc_score(params)
        make_map.make_map(params)
        response.setdefault('res', 'data found')
    else:
        return abort(404)
    return make_response(jsonify(response))

if __name__=='__main__':
    #app.run(host="127.0.0.1", port=5001)
    app.run(host="127.0.0.1", port=5001)
