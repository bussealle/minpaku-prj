import gensim

model = gensim.models.KeyedVectors.load_word2vec_format('/Users/admin/Downloads/ja/ja.bin',binary=True)
print(model.most_similar('営業'))
