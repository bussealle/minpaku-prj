import copy
import math
from pprint import pprint
from gensim import corpora
from gensim import models
from numpy import linalg as LA
from itertools import chain


def normalize(v,axis=-1,order=2):
    l2 = LA.norm(v, ord=order, axis=axis, keepdims=True)
    l2[l2==0] = 1
    return v/l2

def make_tfidf(texts,dictionary):
    def new_idf(docfreq, totaldocs, log_base=2.0, add=1.0):
        return add + math.log(1.0 * totaldocs / docfreq, log_base)

    if not dictionary:
        dictionary = corpora.Dictionary(texts)
    else:
        dictionary.add_documents(texts)
    corpus = list(map(dictionary.doc2bow,texts))
    test_model = models.TfidfModel(corpus,wglobal=new_idf,normalize=False)
    corpus_tfidf = test_model[corpus]
    return corpus_tfidf,dictionary

def make_tfidf_vector(texts,dictionary,super,const):
    objects,dict = make_tfidf(texts=texts,dictionary=dictionary)
    super = [dict.token2id[x] for x in list(set(super))]
    result = {}
    flatten = list(chain.from_iterable(objects))
    for obj in flatten:
        concept,value = obj[0],obj[1]
        d = result.get(obj)
        if not d:
            result[concept] = value
        else:
            result[concept] += value
    for s in super:
        result[s] = result[s]/const
    values = [1.0/x for x in list(result.values())]
    values = normalize(values)
    keys = list(result.keys())
    for i in range(len(keys)):
        result[keys[i]] = values[i]
    return result,dict

if __name__ == '__main__':
    texts = [["祭","冷蔵庫","虹","冷蔵庫"],
            ["祭","電化製品"],
            ["祭","冷蔵庫"]]
    result,dict = make_tfidf_vector(texts=texts,dictionary=None,super=['冷蔵庫'],const=0.5)
    id_to_concept = {}
    for k,v in dict.token2id.items():
        id_to_concept[v] = k
    ans = [(id_to_concept[x[0]],x[1]) for x in list(result.items())]
    pprint(ans)
    pprint(sum([x[1]*x[1] for x in ans]))
