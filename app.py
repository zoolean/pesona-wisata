from flask import Flask, render_template, request, jsonify, redirect,url_for, make_response
from pymongo import MongoClient
from bson import ObjectId
from bson.objectid import ObjectId
import requests
import jwt
from datetime import datetime,timedelta
import hashlib
from werkzeug.utils import secure_filename
import logging
from os.path import join, dirname
from dotenv import load_dotenv
from babel.numbers import format_currency
import os
from services.usersignin import *

app = Flask(__name__)

client = MongoClient("mongodb://test:test@ac-9y5jwii-shard-00-00.vhjxjzx.mongodb.net:27017,ac-9y5jwii-shard-00-01.vhjxjzx.mongodb.net:27017,ac-9y5jwii-shard-00-02.vhjxjzx.mongodb.net:27017/?ssl=true&replicaSet=atlas-skl9qe-shard-0&authSource=admin&retryWrites=true&w=majority")

db = client.pesona_wisata

SECRET_KEY = "PESONAWISATA"
TOKEN_KEY = 'mytoken'

@app.route('/', methods = ['GET'])
def main():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('index.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)


# routing ke halaman login
@app.route('/signin')
def signin():
    return render_template('login.html')

#log in user
@app.route('/sign_in', methods=['POST'])
def sign_in():
    signin
    # email = request.form["email"]
    # password = request.form["password"]
    # print(email)
    # pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    # print(pw_hash)
    # result = db.users.find_one(
    #     {
    #         "email": email,
    #         "password": pw_hash,
    #     }
    # )
    # if result:
    #     payload = {
    #         "id": email,
    #         "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    #     }
    #     token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    #     return jsonify(
    #         {
    #             "result": "success",
    #             "token": token,
    #         }
    #     )
    # else:
    #     return jsonify(   
    #         {
    #             "result": "fail",
    #             "msg": "We could not find a user with that id/password combination",
    #         }
    #     )

# routing ke halaman register
@app.route('/signup')
def signup():
    return render_template('register.html')

# register user
@app.route('/sign_up/save', methods = ['POST'])
def sign_up():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password. encode('utf-8')).hexdigest()
    doc = {
        "name" : name,
        "email" : email,
        "category" : 'visitor',
        "password" : password_hash                                          
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# <<        DOMESTIC    USER        >>
# Menampilkan Data Domestic untuk User
@app.route('/domestic', methods=['GET'])
def get_domestic():
    domestic = db.domestic.find()
    domestic_list = []
    for attraction in domestic:
        domestic_list.append({
            'id': str(attraction['_id']),
            'name': attraction['name'],
            'description': attraction['description'],
            'image_domestic' : attraction['image_domestic'],
            'total_tickets': attraction['total_tickets']
        })
    return jsonify(domestic_list), 200

# Menampilkan Detail Domestic untuk User
@app.route('/domestic/<domestic_id>', methods=['GET'])
def get_domestic_detail(domestic_id):
    attraction = db.domestic.find_one({'_id': ObjectId(domestic_id)})
    token_receive = request.cookies.get(TOKEN_KEY)
    logged_in = False
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        if attraction:
            return render_template('detail-domestic.html', attraction = attraction, user_info=user_info, logged_in = logged_in, is_admin = is_admin)
        else:
            return render_template('detail-domestic.html', user_info=user_info, logged_in = logged_in)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('detail-domestic.html', attraction = attraction, msg=msg)


#book ticket domestic
@app.route('/domestic/book', methods=['POST'])
def book_ticket():
    attraction_id = request.form.get('attraction_id')
    num_tickets = int(request.form.get('num_tickets'))
    name = request.form.get('name')
    email = request.form.get('email')

    if not attraction_id or not num_tickets or not name or not email:
        return jsonify({'message': 'Attraction ID, number of tickets, visitor name, and visitor email are required'}), 400

    # Check ketersediaan domestic
    attraction = db.domestic.find_one({'_id': ObjectId(attraction_id)})
    domestic = attraction['name']
    location = attraction['location']
    if not attraction:
        return jsonify({'message': 'Attraction not found'}), 404

    # Check ketersediaan tiket
    total_tickets = attraction.get('total_tickets', 0)
    if num_tickets > total_tickets:
        return jsonify({'message': 'Not enough available tickets'}), 400

    # Update sisa tiket setelah di booking
    updated_tickets = total_tickets - num_tickets
    db.domestic.update_one({'_id': ObjectId(attraction_id)}, {'$set': {'total_tickets': updated_tickets}})

    price = attraction.get('price', 0)
    total_price = price * num_tickets
    formatted_price = format_currency(total_price, 'IDR', locale='id_ID')

    # Record data booking tiket pengunjung
    db.bookings.insert_one({
        'attraction_id': attraction_id,
        'location': location,
        'domestic' : domestic,
        'num_tickets': num_tickets,
        'name': name,
        'email': email,
        'total_price' : formatted_price,
        'proof': '',
        'status' : 'Pending'
    })

    return jsonify({'message': 'Ticket booked successfully'}), 200


# <<        INTERNATIONAL   USER        >>
# Menampilkan Data International untuk User
@app.route('/international')
def get_international():
    international = db.international.find()
    international_list = []
    for attraction in international:
        international_list.append({
            'id': str(attraction['_id']),
            'name': attraction['name'],
            'description': attraction['description'],
            'image_international' : attraction['image_internationala'],
            'total_tickets': attraction['total_tickets']
        })
    return jsonify(international_list), 200 

# Menampilkan Detail International untuk User
@app.route('/international/<international_id>', methods=['GET'])
def get_international_detail(international_id):
    attraction = db.international.find_one({'_id': ObjectId(international_id)})
    token_receive = request.cookies.get(TOKEN_KEY)
    logged_in = False
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        if attraction:
            return render_template('detail-international.html', attraction = attraction, user_info=user_info, logged_in = logged_in, is_admin = is_admin)
        else:
            return render_template('detail-international.html', user_info=user_info, logged_in = logged_in)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('detail-international.html', attraction = attraction, msg=msg)

#book ticket international



  
    


@app.route('/pesanan')
def pesanan():
    return render_template('pesanan.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

#   <<      DOMESTIC    ADMIN       >>

# Menamppilkan Data Domestic untuk Admin
@app.route('/admin_domestic')
def admin_domestic():
    token_receive = request.cookies.get(TOKEN_KEY)
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"email": payload["id"]})
    admin_info = user_info.get("category") == "admin"
    if admin_info:
        domestic = db.domestic.find()
        domestic_list = []
        for attraction in domestic:
            domestic_list.append({
                'id': str(attraction['_id']),
                'name': attraction['name'],
                'description': attraction['description'],
                'image_domestic' : attraction['image_domestic'],
                'total_tickets': attraction['total_tickets']
            })
        return jsonify("admin-international.html", domestic_list=domestic_list), 200
    
# Menamppilkan Data International untuk Admin
@app.route('/admin_international')
def admin_international():
    token_receive = request.cookies.get(TOKEN_KEY)
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"email": payload["id"]})
    admin_info = user_info.get("category") == "admin"
    if admin_info:
        international = db.international.find()
        international_list = []
        for attraction in international:
            international_list.append({
                'id': str(attraction['_id']),
                'name': attraction['name'],
                'description': attraction['description'],
                'image_international' : attraction['image_international'],
                'total_tickets': attraction['total_tickets']
            })
        return render_template("admin-domestic.html", international_list=international_list), 200

# Tambah Domestic Admin
@app.route('/domestic')
def add_domestic():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    file = request.files['image_domestic']
    extension = file.filename.split('.')[-1]
    filename = f'static/images/wisata-{name}-{mytime}.{extension}'
    file.save(filename)
    price = float(request.form.get('price'))
    formatted_price = format_currency(price, 'IDR', locale='id_ID')
    db.domestic.insert_one({
        'name' : name,
        'description' : description,
        'location' : location,
        'price' : price,
        'price_rupiah' : formatted_price,
        'image_domestic' : filename,
        'total_tickets' : total_tickets,
        
    })
    return jsonify({'message': 'Sukses tambah wisata'}), 201


# Edit Domestic
@app.route('/domestic/<id>', methods=['PUT'])
def edit_domestic(id):
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    # Get data lama dari database
    existing_domestic = db.domestic.find_one({'_id': ObjectId(id)})
    if existing_domestic is None:
        return jsonify({'error': 'Wisata not found'}), 404

    # Handle upload file baru
    file = request.files.get('image_domestic')
    if file:
        # Hapus file lama jika file dirubah
        if 'image_domestic' in existing_domestic:
            existing_file_path = existing_domestic['image_domestic']
            #if os.path.exists(existing_file_path):
            #os.remove(existing_file_path)

        extension = file.filename.split('.')[-1]
        filename = f'static/images/wisata-{name}-{mytime}.{extension}'
        file.save(filename)
    else:
        # Menjaga file jika tidak ada file baru
        filename = existing_domestic.get('image_domestic')

    price = float(request.form.get('price'))
    formatted_price = format_currency(price, 'IDR', locale='id_ID')

    # Update data database
    db.domestic.update_one(
        {'_id': ObjectId(id)},
        {
            '$set': {
                'name': name,
                'description': description,
                'location': location,
                'price': price,
                'price_rupiah' : formatted_price,
                'image_domestic': filename,
                'total_tickets': total_tickets
            }
        }
    )

    return jsonify({'message': 'Sukses edit domestic'}), 200

# Hapus Domestic
@app.route('/domestic/<post_id>', methods=['DELETE'])
def delete_domestic(post_id):
    existing_domestic = db.domestic.find_one({'_id': ObjectId(post_id)})
    existing_file_path = existing_domestic['image_domestic']
    os.remove(existing_file_path)
    result = db.domestic.delete_one({'_id': ObjectId(post_id)})    
    if result.deleted_count > 0:        
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404

#   <<      INTERNATIONAL   ADMIN       >>
# Tambah Wisata International    
@app.route('/international')
def add_international():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    file = request.files['image_international']
    extension = file.filename.split('.')[-1]
    filename = f'static/images/wisata-{name}-{mytime}.{extension}'
    file.save(filename)
    price = float(request.form.get('price'))
    formatted_price = format_currency(price, 'IDR', locale='id_ID')
    db.international.insert_one({
        'name' : name,
        'description' : description,
        'location' : location,
        'price' : price,
        'price_rupiah' : formatted_price,
        'image_international' : filename,
        'total_tickets' : total_tickets,
        
    })
    return jsonify({'message': 'Sukses tambah wisata internasional'}), 201

# Edit International
@app.route('/international/<id>', methods=['PUT'])
def edit_international(id):
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    # Get data lama dari database
    existing_international = db.international.find_one({'_id': ObjectId(id)})
    if existing_international is None:
        return jsonify({'error': 'Wisata not found'}), 404

    # Handle upload file baru
    file = request.files.get('image_international')
    if file:
        # Hapus file lama jika file dirubah
        if 'image_wisata' in existing_international:
            existing_file_path = existing_international['image_international']
            if os.path.exists(existing_file_path): 
               os.remove(existing_file_path)

        extension = file.filename.split('.')[-1]
        filename = f'static/images/wisata-{name}-{mytime}.{extension}'
        file.save(filename)
    else:
        # Menjaga file jika tidak ada file baru
        filename = existing_international.get('image_international')

    price = float(request.form.get('price'))
    formatted_price = format_currency(price, 'IDR', locale='id_ID')

    # Update data database
    db.international.update_one(
        {'_id': ObjectId(id)},
        {
            '$set': {
                'name': name,
                'description': description,
                'location': location,
                'price': price,
                'price_rupiah' : formatted_price,
                'image_international': filename,
                'total_tickets': total_tickets
            }
        }
    )

    return jsonify({'message': 'Sukses edit wisata'}), 200

# Hapus International
@app.route('/international/<post_id>', methods=['DELETE'])
def delete_international(post_id):
    existing_international = db.international.find_one({'_id': ObjectId(post_id)})
    existing_file_path = existing_international['image_international']
    os.remove(existing_file_path)
    result = db.international.delete_one({'_id': ObjectId(post_id)})    
    if result.deleted_count > 0:        
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
