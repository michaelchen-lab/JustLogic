import pandas as pd
from datasets import load_dataset
import jsonlines
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from readability import Readability

def to_words(text):
    words = []
    for i in word_tokenize(text):
        if re.match("^[a-z]*$", i.lower()):
            words.append(i.lower())
    return words

def vocab_count(dataset):
    all_words = []
    if dataset == 'clutrr':
        ds = load_dataset("CLUTRR/v1", "gen_train234_test2to10")
        df = ds['test'].to_pandas()

        for story in df.story:
            all_words.extend(to_words(story))
    
    elif dataset == 'logiqa':
        data = []
        with jsonlines.open('ci_eval/logiQA_2_test.jsonl') as reader:
            for obj in reader:
                data.append(obj)
                qns = "{statement}\n\nOptions:\n(A) {o1}\n(B) {o2}\n(C) {o3}\n(D) {o4}".format(
                    statement=obj['question'],
                    o1 = obj['options'][0],
                    o2 = obj['options'][1],
                    o3 = obj['options'][2],
                    o4 = obj['options'][3],
                )
                obj['question'] = qns
                obj['label'] = obj['answer']
                del obj['answer']
        
        for i in data:
            all_words.extend(to_words(i['text']))
    
    elif dataset == 'justlogic':
        df = pd.read_csv('test_dataset.csv')

        for paragraph in df.paragraph:
            all_words.extend(to_words(paragraph))
        for question in df.question:
            all_words.extend(to_words(question))
    return len(list(set(all_words)))
    
def readability(dataset):
    if dataset == 'justlogic':
        df = pd.read_csv('test_dataset.csv')

        full_string = ''
        for paragraph in df.paragraph:
            full_string += paragraph

        r = Readability(full_string)
        print(r.dale_chall())
    elif dataset == 'folio':
        data = []
        with jsonlines.open('ci_eval/folio_v2_validation.jsonl') as reader:
            for obj in reader:
                data.append(obj)
        full_string = ''
        for i in data:
            full_string += i['premises'].replace('\n', '')
        r = Readability(full_string)
        print(r.dale_chall())

if __name__ == '__main__':
    readability('folio')
    # r = Readability('This is a simple sentence.')
    # print(r.dale_chall())
    