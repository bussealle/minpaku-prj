import MeCab
import sys

def parse_on_mecab(text):
    text = text.replace('（',' ').replace('）',' ')
    mecab = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    mecab.parse('')
    parsed = mecab.parse(text).split('\n')
    result = []
    for p in parsed:
        temp = p.split(',')
        if len(temp)==1:
            continue
        temp = temp[0] + '\t' + temp[1]
        temp = temp.split('\t')
        #FILTERING####
        if len(temp) != 3:
            continue
        if temp[1] != '名詞':
            continue
        if temp[2] == '接尾':
            continue
        ##############
        result.append(temp[0])
    return result

if __name__ == '__main__':
    text = '祭礼（花祭）用の切り紙（梵天）'
    text = text.replace('（',' ').replace('）',' ')
    mecab = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    mecab.parse('')#文字列がGCされるのを防ぐ
    parsed = mecab.parse(text).split('\n')
    print(parsed)
    result = []
    for p in parsed:
        temp = p.split(',')
        if len(temp)==1:
            continue
        temp = temp[0] + '\t' + temp[1]
        temp = temp.split('\t')
        if len(temp) != 3:
            continue
        if temp[1] == '助詞':
            continue
        if temp[2] == '接尾':
            continue
        result.append(temp)
    print(result)
