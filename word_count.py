#%%
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os



s_date_set = ["2019.06.01", "2019.06.08", "2019.06.15", "2019.06.22", "2019.06.29", \
              "2019.07.06", "2019.07.13", "2019.07.20", "2019.07.27", "2019.08.03", \
              "2019.08.10", "2019.08.17", "2019.08.24", "2019.08.31", "2019.09.07", \
              "2019.09.14", "2019.09.21", "2019.09.28", "2019.10.05", "2019.10.12", \
              "2019.10.19", "2019.10.26", "2019.11.02", "2019.11.09", "2019.11.16", \
              "2019.11.23", "2019.11.30", "2019.12.07", "2019.12.14", "2019.12.21", \
              "2019.12.28", "2020.01.04", "2020.01.11", "2020.01.18", "2020.01.25", \
              "2020.02.01", "2020.02.08", "2020.02.15", "2020.02.22", "2020.02.29", \
              "2020.03.07", "2020.03.14", "2020.03.21", "2020.03.28", "2020.04.04", \
              "2020.04.11", "2020.04.18", "2020.04.25", "2020.05.02", "2020.05.09", \
              "2020.05.16", "2020.05.23"]

e_date_set = ["2019.06.07", "2019.06.14", "2019.06.21", "2019.06.28", "2019.07.05", \
              "2019.07.12", "2019.07.19", "2019.07.26", "2019.08.02", "2019.08.09", \
              "2019.08.16", "2019.08.23", "2019.08.30", "2019.09.06", "2019.09.13", \
              "2019.09.20", "2019.09.27", "2019.10.04", "2019.10.11", "2019.10.18", \
              "2019.10.25", "2019.11.01", "2019.11.08", "2019.11.15", "2019.11.22", \
              "2019.11.29", "2019.12.06", "2019.12.13", "2019.12.20", "2019.12.27", \
              "2020.01.03", "2020.01.10", "2020.01.17", "2020.01.24", "2020.01.31", \
              "2020.02.07", "2020.02.14", "2020.02.21", "2020.02.28", "2020.03.06", \
              "2020.03.13", "2020.03.20", "2020.03.27", "2020.04.03", "2020.04.10", \
              "2020.04.17", "2020.04.24", "2020.05.01", "2020.05.08", "2020.05.15", \
              "2020.05.22", "2020.05.29"]

def crawler(maxpage, query, week_num):
    """
    query: 찾고자 하는 단어 (예를들면, 미디어, 기업, 등등)
    week_num: 현재 주 index로 표시
    save_dir: 어디로 저장할 지
    find_words_arr: dataframe로 부터 similar words를 찾을 array를 추출한 다음 parameter로 사용을 원칙
    """
    # maxpage = str(max_pages)
    s_from = s_date_set[week_num].replace(".", "")
    e_to = e_date_set[week_num].replace(".", "")
    page = 1
    maxpage_t = (int(maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지 ...81=9페이지 , 91=10페이지, 101=11페이지
    # f = open(RESULT_PATH + filename, 'w', encoding='utf-8-sig')
    results_list = []
    print('loading query={}'.format(query))
    # Crawl and parse
    while page < maxpage_t:
        print(page-1, end='')
        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=0&ds=" + s_from + "&de=" + e_to + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
            page)
        req = requests.get(url)
        # print(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')
        # print(soup)
        for urls in soup.select("._sp_each_url"):
            try:
                # print(urls["href"])
                # num_chkin = 0 #tmp aks 200609
                if urls["href"].startswith("https://news.naver.com"):
                    # num_chkin += 1
                    # print(urls["href"])
                    # news_detail = get_news(urls["href"])
                    n_url = urls["href"]
                    print('.', end='')
                    news_detail = []
                    breq = requests.get(n_url)
                    bsoup = BeautifulSoup(breq.content, 'html.parser')
                    title = bsoup.select('h3#articleTitle')[0].text  # 대괄호는 h3#articleTitle 인 것중 첫번째 그룹만 가져오겠다.
                    news_detail.append(title)
                    pdate = bsoup.select('.t11')[0].get_text()[:11]
                    news_detail.append(pdate)
                    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
                    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
                    news_detail.append(btext.strip())
                    news_detail.append(n_url)
                    pcompany = soup.select('#footer address')[0].a.get_text()
                    news_detail.append(pcompany)
                    # pdate, pcompany, title, btext
                    results_list.append((news_detail[1], news_detail[0], news_detail[2]))  # date, title, contents
                    # f.write("{}\t{}\t{}\t{}\t{}\n".format(news_detail[1], news_detail[4], news_detail[0], news_detail[2],news_detail[3])) # new style
                # else:
                #     break
            except Exception as e:
                # print(e)
                continue
        page += 10
    df = pd.DataFrame(results_list, columns=['date', 'title', 'contents'])
    print('\nFinished!\n')
    return df

def word_count(df, word_arr):
    result = []
    for word in word_arr:
        count = 0
        for idx, row in df.iterrows():
            count += row['contents'].count(word[0])
        result.append((word[0], count))
    return result
    #df = pd.DataFrame(result, columns=['word', 'count'])

def is_relevant_word(similar_word):
    return similar_word[1] > 0.9 and len(similar_word[0]) > 1

def relevant_words(row):
    temp = []
    for similar_word in row['similar_words']:
        if is_relevant_word(similar_word):
            temp.append(similar_word)
    return temp

queries = ['미디어']#, '소매', '통신', '보험', '금융', '소비재']

df = pd.read_pickle('./word_similar_list.pkl').dropna()

maxpage = '2'

save_dir = 'res_wordCounts'

result = []
for i in range(2):
    print('WEEK {}'.format(i+1))
    for query in queries:
        df_sites = crawler(maxpage, query, i)

        for idx, row in df.iterrows():
            if int(row['week_num'][1:]) - 1 == i:
                words = word_count(df_sites, relevant_words(row))
                result.append((i, query, row['query'], row['word_similar'], words))

df_wordCounts = pd.DataFrame(result, columns=['week', 'industry', 'initial_query', 'word_similar', 'word_counts'])
#df_wordCounts.to_pickle('./word_counts.pkl')

# %%
