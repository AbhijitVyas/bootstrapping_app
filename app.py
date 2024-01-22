import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, url_for, redirect, session
from flask_restful import Resource, Api, reqparse
import json
from mongodb_interface import dockerMongoDB
import bcrypt

records = dockerMongoDB()
app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/bootstrapping", methods=["POST", "GET"])
def bootstrapping():
    if request.method == "POST":
        task_def = request.form["task_def"]
        return redirect(url_for('contents', task_def=task_def))
    else:
        return render_template("bootstrapping.html")

@app.route("/contents", methods=["POST", "GET"])
def contents():
    if request.method == "GET":
        task_def = request.args['task_def']
        response = load_task_definition_to_nlp(task_def)
        return render_template("contents.html", response=response, task_def=task_def)
    else:
        return render_template("select_primitives.html")

@app.route('/select_primitives', methods=['GET', 'POST'])
def select_primitives():
    # TODO: once primitives are selected, draw a DAG graph and show it on the html page with sequence to arrows
    return render_template('select_primitives.html')

# This method will take string and output the action core json instance and store the string as well as action core
# in mongodb
def load_task_definition_to_nlp(task_def: str):
    json_str = {}
    if task_def.__contains__("pour"):
        json_str = ('{"action_verb": "pouring", "substance": "water", '
                    '"source_object": "cup", "target_object": "bowl",'
                    '"unit": "ml", "goal": "pour without spilling", "motion_verb": "tilting", "amount": "50"}')

    elif task_def.__contains__("cut"):
        json_str = ('{"action_verb": "cutting", "substance": "", '
                    '"source_object": "knife", "target_object": "bread",'
                    '"unit": "slice", "goal": "cut without damage", "motion_verb": "slicing", "amount": "5"}')

    data = json.loads(json_str)
    return data


############### mongodb ##################
# assign URLs to have a particular route
@app.route("/register", methods=['post', 'get'])
def index():
    message = ''
    # if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            # insert it in the record collection
            records.insert_one(user_input)

            # find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('register.html')



if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=5000)

