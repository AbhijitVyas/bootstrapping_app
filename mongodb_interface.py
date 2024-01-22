from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
import bcrypt

# set app as a Flask instance
app = Flask(__name__)
# encryption relies on secret keys so they could be run
app.secret_key = "testing"


# #connect to your Mongo DB database
def MongoDB():
    client = MongoClient("mongodb+srv://db:pw@cluster0-xth9g.mongodb.net/Richard?retryWrites=true&w=majority")
    db = client.get_database('total_records')
    records = db.register
    return records


# records = MongoDB()


##Connect with Docker Image###
def dockerMongoDB():
    client = MongoClient(host='test_mongodb',
                         port=27017,
                         username='root',
                         password='pass',
                         authSource="admin")
    db = client.users
    pw = "test123"
    hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    records = db.register
    records.insert_one({
        "name": "Test Test",
        "email": "test@yahoo.com",
        "password": hashed
    })
    return records


#records = dockerMongoDB()


