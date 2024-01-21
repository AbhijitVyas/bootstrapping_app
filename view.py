import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
import json

app = Flask(__name__)


@app.route('/index')
def home():
    return render_template('index.html')

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

