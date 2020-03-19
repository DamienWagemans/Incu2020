from pymongo import ReturnDocument
from config import URL
from flask_pymongo import PyMongo
from flask import Flask, request, render_template, json, jsonify
from bson import json_util


app = Flask(__name__, template_folder='template')
app.config["MONGO_URI"] = URL

json.dumps = json_util.dumps


mongo = PyMongo(app)



@app.route("/<switch_name>/interfaces.html", methods=["GET"])
def get_interfaces_html(switch_name):
    mongo_filter = {'Switch_name': switch_name}
    result = mongo.db.interfaces.find(mongo_filter)
    return render_template('interfaces.html', result=result)

@app.route("/<switch_name>/interfaces.json", methods=["GET"])
def get_interfaces_json(switch_name):
    mongo_filter = {'Switch_name': switch_name}
    result = mongo.db.interfaces.find(mongo_filter)
    return jsonify(result), 200

@app.route("/<switch_name>/<interface_name>/details.html", methods=["GET"])
def get_interface_detail_html(switch_name, interface_name):
    # in this case, interface name countains / , so I replace all / in the interface name by .
    # here is an example : http://127.0.0.1:5000/Switch1/g0.1/details.html
    interface_name_ok = interface_name.replace('.', '/')
    mongo_filter = {'Switch_name': switch_name, 'Interface_Name': interface_name_ok}
    result = mongo.db.interfaces.find(mongo_filter)
    return render_template('interface_detail.html', result=result)

@app.route("/<switch_name>/<interface_name>/details.json", methods=["GET"])
def get_interface_detail_json(switch_name, interface_name):
    # in this case, interface name countains / , so I replace all / in the interface name by .
    # here is an example : http://127.0.0.1:5000/Switch1/g0.1/details.json
    interface_name_ok = interface_name.replace('.', '/')
    mongo_filter = {'Switch_name': switch_name, 'Interface_Name': interface_name_ok}
    result = mongo.db.interfaces.find(mongo_filter)
    return jsonify(result), 200

@app.route("/<switch_name>/<interface_name>", methods=["PATCH"])
def update_interface_description(switch_name, interface_name):
    interface_name_ok = interface_name.replace('.', '/')
    payload = request.get_json()
    if payload:
        if ('State') in payload.keys():
            if(payload['State'] not in ['Down', 'Up', 'down', 'up', 'DOWN', 'UP']):
                return 'Error, State is not valid', 500
        result = mongo.db.interfaces.find_one_and_update(
            {'Switch_name': switch_name, 'Interface_Name': interface_name_ok},
            {'$set': payload},
            return_document=ReturnDocument.AFTER
        )
        return jsonify(result), 200
    return 'Error', 500


if __name__ == '__main__':
    app.run()



