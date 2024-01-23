import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
import json
import subprocess
import base

app = Flask(__name__)


@app.route('/index')
def home():
    return render_template('index.html')

@app.route("/bootstrapping", methods=["POST", "GET"])
def bootstrapping():
    if request.method == "POST":
        task_def = request.form["task_def"]
        ### Trigger base.py by passing NL instruction(task_def) as param

        intent, rasa_dict = base.main(task_def)
        rasa_dict_str = json.dumps(rasa_dict)
        print("RASA OUTPUT: ",rasa_dict)
        return redirect(url_for('contents', task_def=task_def, intent = intent, inputs=rasa_dict_str))
    else:
        return render_template("bootstrapping.html")

@app.route("/contents", methods=["POST", "GET"])
def contents():
    if request.method == "GET":
        task_def = request.args['task_def']
        rasa_str = request.args.get('inputs', '{}')
        rasa_intent = request.args['intent']
        
        response = load_task_definition_to_nlp(rasa_intent,rasa_str)
        return render_template("contents.html", response=response, task_def=task_def)
    else:
        return render_template("select_primitives.html")

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

