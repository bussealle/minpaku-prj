import json
import numpy as np
from pprint import pprint
from gensim.corpora import Dictionary
from somoclu import Somoclu
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA


if __name__=='__main__':
    dict_name = 'dictionary.dct'
    dictionary = Dictionary.load(dict_name)
    dict_len = len(dictionary.keys())

    with open('log_calc.json','r') as f :
        log_calc = json.load(f)

    result = []
    id_vec = []
    for key in log_calc.keys():
        for k,v in log_calc[key].items():
            for id in v['id']:
                if not id in id_vec:
                    id_vec.append(id)

    for i in id_vec:
        result.append(np.zeros(dict_len))

    for key in log_calc.keys():
        for k,v in log_calc[key].items():
            for id in v['id']:
                j = id_vec.index(id)
                result[j][int(k)] += v['data']

    # データを読み込む
    dataset = load_iris()
    X = dataset.data
    y = dataset.target

    # SOMに入れる前にPCAして計算コスト削減を測る（iris程度では無駄）
    pca = PCA(n_components=0.95)
    X = pca.fit_transform(X)

    # SOMの定義
    n_rows = 16
    n_cols = 24
    som = Somoclu(n_rows=n_rows, n_columns=n_cols,
                  initialization="pca", verbose=2)

    # 学習
    som.train(data=X, epochs=1000)

    # U-matrixをファイル出力
    som.view_umatrix(labels=y, bestmatches=True,
                     filename="umatrix.png")
