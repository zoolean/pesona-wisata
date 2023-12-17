from flask import Flask, render_template, request, jsonify, redirect,url_for, make_response 
import hashlib
from babel.numbers import format_currency
from datetime import datetime, timedelta
import jwt
from app import SECRET_KEY, db
def signin():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print(pw_hash)
    result = db.users.find_one(
        {
            "email": email,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )