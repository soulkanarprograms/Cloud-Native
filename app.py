from flask import Flask, request, jsonify
from flask import abort
from flask import make_response, url_for

import json
import sqlite3
from time import gmtime, strftime

app = Flask(__name__)


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)


@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/api/v1/info")
def home_index():
    conn = sqlite3.connect('cloud.db')
    print("Opened database successfully");
    api_list=[]
    cursor = conn.execute("SELECT buildtime, version, methods, links from apirelease")

    for row in cursor:
        a_dict = {}
        a_dict['version'] = row[0]
        a_dict['buildtime'] = row[1]
        a_dict['methods'] = row[2]
        a_dict['links'] = row[3]
        api_list.append(a_dict)
    conn.close()

    return jsonify({'api_version': api_list}), 200


def list_users():
    conn = sqlite3.connect('cloud.db')
    print("Opened database successfully")
    api_list=[]
    cursor = conn.execute("SELECT username, full_name, email, password, id from users")

    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['email'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)

    conn.close()
    return jsonify({'user_list': api_list})


def list_user(user_id):
    conn = sqlite3.connect('cloud.db')
    print("Opened database successfully")
    cursor = conn.execute("SELECT * FROM users WHERE id=?", (user_id,))

    data = cursor.fetchall()
    user = {}
    if len(data) != 0:
        user['username'] = data[0][0]
        user['name'] = data[0][1]
        user['email'] = data[0][2]
        user['password'] = data[0][3]
        user['id'] = data[0][4]

    conn.close()
    return jsonify(user)


def add_user(new_user):
    conn = sqlite3.connect('cloud.db')
    print("Opened database successfully");

    cursor = conn.cursor()
    cursor.execute("SELECT * from users where username=? or email=?", (new_user['username'], new_user['email'], ))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute("insert into users (username, email, password, full_name) values(?,?,?,?)",
                       (new_user['username'], new_user['email'], new_user['password'], new_user['name']))
        conn.commit()
        return "Success"

    conn.close()
    return jsonify("")


@app.route("/api/v1/users", methods=['GET'])
def get_users():
    return list_users()


@app.route("/api/v1/users/<int:user_id>", methods=['GET'])
def get_user(user_id):
    return list_user(user_id)


@app.route("/api/v1/users", methods=['POST'])
def create_users():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'email': request.json['email'],
        'name': request.json['name'],
        'password': request.json['password'],
    }
    return jsonify({'status': add_user(user)}), 201

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
