import itertools
import string
import nltk
# nltk.download('punkt')
# nltk.download('wordnet')
from nltk import word_tokenize
from nltk.corpus import wordnet as wn
import spacy

color = ['color.n.01']
size = ['size.n.01']
material = []
shape = ['shape.n.01']
consistency = ['consistency.n.01']
dimensions = ['mass','length','temperature']

def compounds(sentence):
        instr = word_tokenize(sentence)
        newinstr = []
        i = 0
        for _ in instr:
            found = False
            if i < len(instr):
                stop = ''
                # check three-word compounds
                for x in itertools.product('_-', repeat=2):
                    tmpword = '{}{}{}{}{}'.format(instr[i], x[0], instr[min(len(instr)-1, i+1)],
                                                  x[1], instr[min(len(instr)-1, i+2)])
                    # this is hack for the concept on_the_table
                    if len(wn.synsets(tmpword)) > 0 and tmpword != 'on_the_table':  
                        newinstr.append(tmpword+stop)
                        found = True
                        i += 3
                        break
                # check two-word compounds
                if not found:
                    for y in ['_', '-']:
                        tmpword = '{}{}{}'.format(instr[i], y, instr[min(len(instr)-1, i+1)])
                        if len(wn.synsets(tmpword)) > 0:
                            newinstr.append(tmpword+stop)
                            found = True
                            i += 2
                            break
                # leave current word as it is
                if not found:
                    newinstr.append(instr[i])
                    i += 1
            else:
                i+=1
        # untokenize sentence before returning.
        return "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in newinstr]).strip()


def verb_detection(inputs):
    dicts ={}
    valid_verb_tags = ['VB', 'VBG', 'VBZ', 'VBD', 'VBN', 'VBP']
    valid_adverb_tags = ['RB', 'RBR', 'RBS', 'WRB']

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(inputs)

    for token in doc:
        if token.tag_ in valid_verb_tags:
            if token.pos_ not in dicts:
                dicts[token.pos_] = {token.text:token.dep_}
            else:
                dicts[token.pos_].update({token.text:token.dep_})
        elif token.tag_ in valid_adverb_tags:
            if token.pos_ not in dicts:
                dicts[token.pos_] = {token.text:token.dep_}
            else:
                dicts[token.pos_].update({token.text:token.dep_})

    return dicts

def preprocessing(instruction):

    # instruction = "bring the small cup from the brown shelf"
    text = compounds(instruction)

    # download models -> python -m spacy download en_core_web_sm
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(instruction)
    doc2 = nlp(text)

    dicts = {}
    for token in doc:
        if token.dep_=="amod":
            # todo only add amod's with high similarity with size,shape,color,consistency using wordnet
            if not token.head.text in dicts:
                dicts[token.head.text] = [token.text]
                dicts[token.head.text] = list(set(dicts[token.head.text]))
            else:
                dicts[token.head.text].append(token.text)
                dicts[token.head.text] = list(set(dicts[token.head.text]))

    # doc2 contains compounded tokens if present in user input
    for token in doc2:
        if token.dep_=="amod":
            # todo only add amod's with high similarity with size,shape,color,consistency using wordnet
            simples = " ".join(str(token.head.text).split('_'))
            if not simples in dicts:
                dicts[simples] = [token.text]
                dicts[simples] = list(set(dicts[simples]))
            else:
                dicts[simples].append(token.text)
                dicts[simples] = list(set(dicts[simples]))

    cdict = {}
    for token in doc:
        if token.dep_ == 'compound':
            complete_word = token.text + " " + token.head.text
            if not complete_word in cdict:
                cdict[complete_word] = token.head.text

        # print(token.text, token.dep_, token.head.text, token.pos_, token.tag_)

    verbals = verb_detection(instruction)

    # print("Props in preprocessing : ",[toks for toks in text.split(" ") if '_' in toks])

    return {'compounded_text': text, 'props': dicts, 'verbs': verbals, 'compounds_words': cdict}
# for token in doc:
    # print(token.text, token.dep_, token.head.text, token.pos_)

