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

class RASA:
    def __init__(self, nl_instruction: str, intent: str, resources: dict):
        self.nl_instruction = nl_instruction
        self.intent = intent
        self.resources = resources


RASA_outputs = []

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
        intent, rasa_dict = base.main(task_def)         # -------> Calling RASA server with input instruction(task_def)
        RASA_outputs.append(RASA(task_def, intent, rasa_dict))  # ---> Saving RASA output as RASA instance in list
        return redirect(url_for('contents'))
    else:
        try:
            RASA_outputs.clear()                                                      # -------> Clearing RASA_outputs[]
            session.clear()                                                             # -------> Clearing session data
        except:
            print("Cleared or No session to clear")
        return render_template("bootstrapping.html")


@app.route("/contents", methods=["POST", "GET"])
def contents():
    if request.method == "GET":
        modified = session.get('modified_rasa_response',None)
        if modified is None:
            try:
                data = RASA_outputs[0]
                response = load_task_definition_to_nlp()
                session['rasa_response'] = response
                return render_template("contents.html", response=response, task_def=data.nl_instruction)
            except:
                print("problem rendering contents template page")
        else:
            session['rasa_response'] = modified
            return render_template("contents.html", response=modified, task_def=RASA_outputs[0].nl_instruction)
    else:
        if request.form['submit_button'] == 'Edit':
            return redirect(url_for('edit_contents'))
        elif request.form['submit_button'] == 'Next':
            mongo_save = session['rasa_response']
            connectToMongo(mongo_save)                                    # ------> Calling Mongo function to store data
            print(mongo_save)
            ### remove prim_dix
            prim_dix = {}
            prim_dix['source'] = mongo_save['source_object']
            prim_dix['destination'] = mongo_save['target_object']
            try:
                data = RASA_outputs[0]
                primitives = provide_primitive_list(rasa_content=prim_dix, intent=data.intent)
                # primitives = provide_primitive_list(rasa_content=data.resources, intent=data.intent)
                return render_template('select_primitives.html', len=len(primitives), primitives=primitives)
            except:
                print("problem rendering select_primitives template page")


@app.route("/edit_contents", methods=["GET","POST"])
def edit_contents():
    if request.method == "GET":
        response = session.get('rasa_response', None)
        if RASA_outputs and response is not None:
            data = RASA_outputs[0]
            return render_template("edit_contents.html", response=response, task_def=data.nl_instruction)
        else:
            return render_template("edit_contents.html")
    else:
        modified_rasa_response = {key: request.form[key] for key in request.form}
        print("MODIFIED FORM : ", modified_rasa_response)
        session['modified_rasa_response'] = modified_rasa_response
        return redirect(url_for('contents'))


@app.route('/select_primitives', methods=['GET', 'POST'])
def select_primitives():
    rasa_content = {"action_verb": "pour", "source": "cup", "destination": "bowl"}
    primitives = provide_primitive_list(rasa_content, intent="Pouring")
    return render_template('select_primitives.html', primitives=primitives)


def provide_primitive_list(rasa_content: dict, intent: str):
    if 'pour' in intent.lower():
        return [{"primitive_action": "PickUp", "constraint": rasa_content["source"]},
                {"primitive_action": "Align", "constraint": rasa_content["destination"]},
                {"primitive_action": "Tilt", "constraint": rasa_content["source"]},
                {"primitive_action": "PutDown", "constraint": rasa_content["source"]}]
    elif 'cut' in intent.lower():
        return [{"primitive_action": "PickUp", "constraint": rasa_content["source"]},
                {"primitive_action": "Align", "constraint": rasa_content["destination"]},
                {"primitive_action": "Cut", "constraint": rasa_content["destination"]},
                {"primitive_action": "PutDown", "constraint": rasa_content["source"]}]
    elif 'shake' in intent.lower():
        return [{"primitive_action": "PickUp", "constraint": rasa_content["source"]},
                {"primitive_action": "Align", "constraint": rasa_content["destination"]},
                {"primitive_action": "Shake", "constraint": rasa_content["source"]},
                {"primitive_action": "PutDown", "constraint": rasa_content["source"]}]
    else:
        return []

def load_task_definition_to_nlp():
    json_dict = {}
    if RASA_outputs:
        data = RASA_outputs[0]                                     # -------> Accessing the saved instance of RASA class
        intent = data.intent                                  # -------> intent :  intent detected by the RASA framework
        resources = data.resources        # -------> resources : dict of rasa extraction info (source,destination etc.,)
        print("INSIDE", type(resources), resources)
        if not 'error' in resources:
            if intent == "pouring":
                json_dict = {"action_verb": "Pouring", "substance": resources["substance"], "source_object": resources["source"],
                         "target_object": resources["destination"], "unit": resources["units"], "goal": resources["goal"],
                         "motion_verb": resources["motion"], "amount": resources["amount"]}
            elif intent == "shake":
                json_dict = {"action_verb": "Shaking", "substance": "", "source_object": resources["obj_to_be_shaken"],
                         "target_object": resources["destination"], "unit": resources["units"], "goal": resources["goal"],
                         "motion_verb": resources["motion"], "amount": resources["amount"]}
        else:
            json_dict = resources
        print("ANSWER: ", json_dict)

    return json_dict

# This method will read RASA intent and resources and save it in MongoDB
def connectToMongo(mongo_save: dict):
    try:
        # client = pymongo.MongoClient("mongodb://mongoc:27017/")
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client['bootstrap']
        collection = db['InputInstructions']
        if RASA_outputs:
            data = RASA_outputs[0]
            mongodata = {'NL_instruction': data.nl_instruction,
                    'Info_Extracted': mongo_save}
            result = collection.insert_one(mongodata)
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

