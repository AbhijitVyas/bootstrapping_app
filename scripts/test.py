import spacy
# nlp = spacy.load("en_core_web_sm")
# doc = nlp("pour some tomato paste over cooking pan")
#
# # for token in doc:
# #     print(token.text, token.dep_, token.head.text, token.pos_, token.tag_)
#
# # dicts = {}
# valid_verb_tags = ['VB', 'VBG', 'VBZ', 'VBD', 'VBN', 'VBP']
# valid_adverb_tags = ['RB','RBR','RBS','WRB','VB']
#
# print(bool(set(valid_adverb_tags) & set(valid_verb_tags)))

# for token in doc:
#     if token.tag_ in valid_verb_tags:
#         if token.pos_ not in dicts:
#             dicts[token.pos_] = {token: token.dep_}
#         else:
#             dicts[token.pos_].update({token: token.dep_})
#     elif token.tag_ in valid_adverb_tags:
#         if token.pos_ not in dicts:
#             dicts[token.pos_] = {token: token.dep_}
#         else:
#             dicts[token.pos_].update({token: token.dep_})

# dicts = {}
#
# for token in doc:
#     if token.dep_=="amod":
#         if not token.head.text in dicts:
#             dicts[token.head.text] = [token.text]
#         else:
#             dicts[token.head.text].append(token.text)
# print(dicts)
# #----------------------------------------------------------------------------------------------------------------------
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer
#
# lemmatizer = WordNetLemmatizer()
# stemmer = PorterStemmer()
# print(stemmer.stem("fruits"))
# print(lemmatizer.lemmatize("squared"))

# print(" ".join("chicken".split('_')))
#----------------------------------------------------------------------------------------------------------------------
import requests
import os
import json

api_key = os.environ.get('API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}

data = {
    "contents": [{
        "parts": [{
            "text": "what is your name"
        }]
    }]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
resp = response.json()
print(resp)
# print(resp['candidates'][0]['content']['parts'][0]['text'])
