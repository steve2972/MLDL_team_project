import pandas as pd
import numpy as np
import gensim
from gensim import utils
from konlpy.tag import Okt
from gensim.models import Word2Vec
import logging
from gensim.test.utils import get_tmpfile

logger = logging.getLogger(__name__)

datafile = pd.read_csv('Stopwords_Korean.csv')
stopWordsKorean = datafile['words']
datafile = pd.read_csv('Wordlist_Korean.csv')
similarWords = datafile['words']


def word2vec2tensor(word2vec_model, tensor_filename, binary=False):
    model = word2vec_model
    outfiletsv = tensor_filename + '_tensor.tsv'
    outfiletsvmeta = tensor_filename + '_metadata.tsv'

    with utils.open(outfiletsv, 'wb') as file_vector, utils.open(outfiletsvmeta, 'wb') as file_metadata:
        for word in model.index2word:
            file_metadata.write(gensim.utils.to_utf8(word) + gensim.utils.to_utf8('\n'))
            vector_row = '\t'.join(str(x) for x in model[word])
            file_vector.write(gensim.utils.to_utf8(vector_row) + gensim.utils.to_utf8('\n'))

    logger.info("2D tensor file saved to %s", outfiletsv)
    logger.info("Tensor metadata file saved to %s", outfiletsvmeta)


def model_train(dataframe, content_col, size=100, window=5):
    okt = Okt()
    result = []
    print('loading ', end='')
    for index, row, in dataframe.iterrows():
        if index % 10 == 0:
            print('. ', end='')
        try:
            tokenlist = okt.pos(row[content_col], stem=True, norm=True)  # 단어 토큰화
        except:
            print(index, end='')
            continue
        temp = []

        i = 0
        while i < len(tokenlist):
            word1, word2 = '', ''
            if i < len(tokenlist) - 2:
                scan = (tokenlist[i][0], tokenlist[i + 1][0], tokenlist[i + 2][0])
                word1 = ''.join(scan)
            if i < len(tokenlist) - 1:
                scan = (tokenlist[i][0], tokenlist[i + 1][0])
                word2 = ''.join(scan)

            if word1 in similarWords.values:
                temp.append(word1)
                i += 2
            elif word2 in similarWords.values:
                temp.append(word2)
                i += 3
            elif tokenlist[i][1] == 'Noun':
                temp.append(tokenlist[i][0])
                i += 1
            else:
                i += 1

        """
        for word in tokenlist:
            if word[1] in ["Noun"]:  # 명사일 때만
                temp.append((word[0]))  # 해당 단어를 저장함
        """

        if temp:  # 만약 이번에 읽은 데이터에 명사가 존재할 경우에만
            result.append(temp)  # 결과에 저장
    print('\nFinished!')

    text = []
    for i in range(len(result)):
        text.append([word for word in result[i] if word not in stopWordsKorean])
        # print(str(len(result[i])-len(text[i])) + " stopwords are eliminated.")

    model = Word2Vec(text, size=size, window=window, min_count=5, workers=4, sg=0)
    return result, model


def print_similar(model_, query):
    try:
        model_result = model_.wv.most_similar(query)
        print(model_result)
        return model_result
    except KeyError:
        print('{} not in model vocabulary. Please try another query.'.format(query))


def create_tensors(model, output):
    word2vec2tensor(model.wv, output)


#df = pd.read_pickle('./res_naverCrawl/data_인공지능_W52.pkl')
#result, model = model_train(df, 'contents')



df = pd.read_pickle('./res_naverCrawl/data_인공지능_W51.pkl')
result, model = model_train(df, 'contents')

print(result)