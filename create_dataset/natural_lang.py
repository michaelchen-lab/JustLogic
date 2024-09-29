from datasets import load_dataset
import numpy as np
from nltk.tokenize import sent_tokenize
from string import punctuation

# ds = load_dataset("wikimedia/wikipedia", "20231101.en", split='train[:1000]')

class SentGen:
    def __init__(self):
        # split='train[:1000]'
        self.ds = load_dataset("community-datasets/generics_kb", "generics_kb_best")
        self.sents = self.ds['train'].to_pandas()
        self.i = list(range(len(self.sents)))
    
    def gen(self, size=1):
        sents = []
        for i in np.random.choice(self.i, size, replace=False):
            sent = self.sents.iloc[int(i)]
            if sent['generic_sentence'][-1] == '.':
                sents.append(sent['generic_sentence'])
            else:
                sents.append(sent['generic_sentence'] + '.')
        return sents

    def gen_similar_sent(self, sent):
        term_search = self.sents[self.sents.generic_sentence == sent]
        if len(term_search) >= 1:
            term = term_search['term'].to_string(index=False)
        else: # a full stop was added in gen()
            term = self.sents[self.sents.generic_sentence == sent[:-1]]['term'].to_string(index=False)
        
        term_sents = self.sents[self.sents.term == term]['generic_sentence'].to_list()
        sents = [s for s in term_sents if s != sent]
        try:
            rand_sent = np.random.choice(sents)
            if rand_sent[-1] == '.':
                return rand_sent
            else:
                return rand_sent+'.'
        except:
            # other sents with the same term
            return self.gen()[0]

if __name__ == '__main__':
    np.random.seed(0)
    sentgen = SentGen()
    print(len(sentgen.sents))
    # sents = sentgen.gen(size=50)
    # print(sents)
    # print(sentgen.gen_similar_sent('A woodland is a biome.'))

# all_sents = []
# for text in ds:
#     print(text.keys())
#     sents = sent_tokenize(text['text'])
#     single_punc_sents = []
#     for sent in sents:
#         puncs = [i for i in sent if i in punctuation]
#         if puncs == ['.'] and '\n' not in sent:
#             single_punc_sents.append(sent)
#     all_sents.append({'id': text['id'], 'sents': single_punc_sents})
#     break

# print(all_sents)

# todo: remove all sentences with >1 punctuation. (prevent sentences with conditionals, etc)