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
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('homepage.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)




# Menampilkan Data Domestic
@app.route('/domestic')
def get_domestic():
    domestic = db.domestic.find()
    domestic_list = []
    for attraction in domestic:
        domestic_list.append({
            'id': str(attraction['_id']),
            'name': attraction['name'],
            'description': attraction['description'],
            'image_wisata' : attraction['image_wisata'],
            'total_tickets': attraction['total_tickets']
        })
    return jsonify(domestic_list), 200

# Tambah Domestic   
@app.route('/domestic')
def add_domestic():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    file = request.files['image_wisata']
    extension = file.filename.split('.')[-1]
    filename = f'static/images/wisata-{name}-{mytime}.{extension}'
    file.save(filename)
    price = float(request.form.get('price'))
    formatted_price = format_currency(price, 'IDR', locale='id_ID')
    db.wisata.insert_one({
        'name' : name,
        'description' : description,
        'location' : location,
        'price' : price,
        'price_rupiah' : formatted_price,
        'image_wisata' : filename,
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
    file = request.files.get('image_wisata')
    if file:
        # Hapus file lama jika file dirubah
        if 'image_wisata' in existing_domestic:
            existing_file_path = existing_domestic['image_wisata']
            #if os.path.exists(existing_file_path):
            #os.remove(existing_file_path)

        extension = file.filename.split('.')[-1]
        filename = f'static/images/wisata-{name}-{mytime}.{extension}'
        file.save(filename)
    else:
        # Menjaga file jika tidak ada file baru
        filename = existing_domestic.get('image_wisata')

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
                'image_wisata': filename,
                'total_tickets': total_tickets
            }
        }
    )

    return jsonify({'message': 'Sukses edit wisata'}), 200

# Hapus Domestic
@app.route('/domestic/<post_id>', methods=['DELETE'])
def delete_domestic(post_id):
    existing_domestic = db.domestid.find_one({'_id': ObjectId(post_id)})
    existing_file_path = existing_domestic['image_wisata']
    os.remove(existing_file_path)
    result = db.domestic.delete_one({'_id': ObjectId(post_id)})    
    if result.deleted_count > 0:        
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404

@app.route('/international')
def international():
    international = db.international.find()
    international_list = []
    for attraction in international:
        international_list.append({
            'id': str(attraction['_id']),
            'name': attraction['name'],
            'description': attraction['description'],
            'image_wisata' : attraction['image_wisata'],
            'total_tickets': attraction['total_tickets']
        })
    return jsonify(international_list), 200 
    
@app.route('/international')
def add_international():
    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    total_tickets = int(request.form.get('total_tickets'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    file = request.files['image_wisata']
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
        'image_wisata' : filename,
        'total_tickets' : total_tickets,
        
    })
    return jsonify({'message': 'Sukses tambah wisata internasional'}), 201

# Edit Domestic
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
    file = request.files.get('image_wisata')
    if file:
        # Hapus file lama jika file dirubah
        if 'image_wisata' in existing_international:
            existing_file_path = existing_international['image_wisata']
            if os.path.exists(existing_file_path): 
                                os.remove(existing_file_path)

        extension = file.filename.split('.')[-1]
        filename = f'static/images/wisata-{name}-{mytime}.{extension}'
        file.save(filename)
    else:
        # Menjaga file jika tidak ada file baru
        filename = existing_international.get('image_wisata')

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
                'image_wisata': filename,
                'total_tickets': total_tickets
            }
        }
    )

    return jsonify({'message': 'Sukses edit wisata'}), 200

# Hapus International
@app.route('/international/<post_id>', methods=['DELETE'])
def delete_international(post_id):
    existing_international = db.international.find_one({'_id': ObjectId(post_id)})
    existing_file_path = existing_international['image_wisata']
    os.remove(existing_file_path)
    result = db.international.delete_one({'_id': ObjectId(post_id)})    
    if result.deleted_count > 0:        
        return jsonify({'message': 'Post deleted successfully'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404



  
    


@app.route('/pesanan')
def pesanan():
    return render_template('pesanan.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
