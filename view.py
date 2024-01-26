import os,sys
from flask import Flask, render_template, jsonify, request, redirect, url_for,session
from flask_restful import Resource, Api, reqparse
import signal
import json
import subprocess
import base
import secrets
import pymongo
import bcrypt
from mongodb_interface import dockerMongoDB

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.secret_key = secret_key

mongo_client_instance,records = dockerMongoDB()

# disconnects,cleanup function are defined and used to disconnect any existing mongodb connections to ensure proper
# flask app termination
def disconnects():
    try:
        mongo_client_instance.close()
        print('Existing MongoDB connection closed')
    except:
        print('Could not close or No available mongodb connection')

def cleanup(signum, frame):
    print(f"Received signal {signum}. Cleaning up resources before termination...")
    disconnects()
    sys.exit(0)


# Register the cleanup function to be called on termination
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route("/bootstrapping", methods=["POST", "GET"])
def bootstrapping():
    if request.method == "POST":
        task_def = request.form["task_def"]
        intent, rasa_dict = base.main(task_def)
        rasa_dict_str = json.dumps(rasa_dict)
        print("RASA OUTPUT: ",rasa_dict)
        return redirect(url_for('contents', task_def=task_def, intent = intent, inputs=rasa_dict_str))
    else:
        try:
            session.clear()
        except:
            print("Cleared or No session to clear")
        return render_template("bootstrapping.html")

@app.route("/contents", methods=["POST", "GET"])
def contents():
    if request.method == "GET":
        modified = session.get('modified_rasa_data',None)
        if modified is None:
            task_def = request.args['task_def']
            rasa_str = request.args.get('inputs', '{}')
            rasa_intent = request.args['intent']

            response = load_task_definition_to_nlp(rasa_intent, rasa_str)
            session['rasaresponse'] = response
            session['task_def'] = task_def
            return render_template("contents.html", response=response, task_def=task_def)
        else:
            session['rasaresponse'] = modified
            task_def = session.get('task_def')
            return render_template("contents.html",response=modified, task_def=task_def)
    else:
        if request.form['submit_button'] == 'Edit':
            return redirect(url_for('edit_contents'))
        elif request.form['submit_button'] == 'Next':
            mongosave = session['rasaresponse']
            inputNL = session['task_def']
            print("IN MONGO dict: ", mongosave)
            connectToMongo(mongosave,inputNL)
            return render_template("select_primitives.html")

@app.route("/edit_contents", methods=["GET","POST"])
def edit_contents():
    if request.method == "GET":
        response = session.get('rasaresponse', None)
        if response is not None:
            task_def = session.get('task_def')
            return render_template("edit_contents.html", response=response, task_def=task_def)
        else:
            return render_template("edit_contents.html")
    else:
        modified_rasa_data = {key: request.form[key] for key in request.form}
        print("MODIFIED FORM : ",modified_rasa_data)
        session['modified_rasa_data'] = modified_rasa_data
        return redirect(url_for('contents'))

@app.route('/select_primitives', methods=['GET', 'POST'])
def select_primitives():
    return render_template('select_primitives.html')

# This method will take string and output the action core json instance and store the string as well as action core
# in mongodb
def load_task_definition_to_nlp(rasa_intent: str,rasa_str: str):
    json_str = {}
    json_dict = {}
    try:
        # Deserialize the JSON string into a dictionary
        rasa_dict = json.loads(rasa_str)
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {str(e)}"

    print("INSIDE", type(rasa_dict), rasa_dict)
    if not 'error' in rasa_dict:
        if rasa_intent=="pouring":
            json_dict = {"action_verb": "Pouring", "substance": rasa_dict["substance"], "source_object": rasa_dict["source"],
                     "target_object": rasa_dict["destination"], "unit": rasa_dict["units"], "goal": rasa_dict["goal"],
                     "motion_verb": rasa_dict["motion"], "amount": rasa_dict["amount"]}
        elif rasa_intent=="shake":
            json_dict = {"action_verb": "Shaking", "substance": "", "source_object": rasa_dict["obj_to_be_shaken"],
                     "target_object": rasa_dict["destination"], "unit": rasa_dict["units"], "goal": rasa_dict["goal"],
                     "motion_verb": rasa_dict["motion"], "amount": rasa_dict["amount"]}
    else:
        json_dict = rasa_dict
    print("ANSWER: ", json_dict)

    # if task_def.__contains__("pour"):
    #     json_str = ('{"action_verb": "pouring", "substance": "water", '
    #                 '"source_object": "cup", "target_object": "bowl",'
    #                 '"unit": "ml", "goal": "pour without spilling", "motion_verb": "tilting", "amount": "50"}')
    #
    # elif task_def.__contains__("cut"):
    #     json_str = ('{"action_verb": "cutting", "substance": "", '
    #                 '"source_object": "knife", "target_object": "bread",'
    #                 '"unit": "slice", "goal": "cut without damage", "motion_verb": "slicing", "amount": "5"}')
    # data = json.loads(json_str)
    # return data
    return json_dict


def connectToMongo(mongosave : dict, inputNL: str):
    try:
        client = pymongo.MongoClient("mongodb://mongoc:27017/")
        # client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['bootstrap']
        collection = db['InputInstructions']
        data = {'NL_instruction': inputNL,
                'Info_Extracted': mongosave}
        result = collection.insert_one(data)
        print("Inserted document ID:", result.inserted_id)
        client.close()
    except:
        print('MongoDB not connected')

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
            # adding them in a dictionary in key value pairs
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

