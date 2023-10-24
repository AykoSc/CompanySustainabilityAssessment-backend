"""
This code has largely been made available by https://huggingface.co/ai-lab/ESGify
"""

import nltk

from flair.data import Sentence
from flair.nn import Classifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')


def process_text_using_ner(text: str):
    # Masking some words using NER
    stop_words = set(stopwords.words('english'))
    tagger = Classifier.load('flair/ner-english-ontonotes')
    tag_list = ['FAC', 'LOC', 'ORG', 'PERSON']

    filtered_sentence = []
    word_tokens = word_tokenize(text)
    # Converts the words in word_tokens to lower case and then checks whether
    # They are present in stop_words or not
    for w in word_tokens:
        if w.lower() not in stop_words:
            filtered_sentence.append(w)
    # Make a sentence
    sentence = Sentence(' '.join(filtered_sentence))
    # Run NER over sentence
    tagger.predict(sentence)
    sent = ' '.join(filtered_sentence)
    new_string = ''
    start_t = 0
    for i in sentence.get_labels():
        info = i.to_dict()
        val = info['value']
        if info['confidence'] > 0.8 and val in tag_list:

            if i.data_point.start_position > start_t:
                new_string += sent[start_t:i.data_point.start_position]
            start_t = i.data_point.end_position
            new_string += f'<{val}>'
    new_string += sent[start_t:-1]

    return new_string
