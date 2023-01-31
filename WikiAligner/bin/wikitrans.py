#TODO: check all paths, if not exists, create automatically.
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.
sys.path.append(BASE_DIR)
datapath = os.path.join(BASE_DIR, 'data')
if not os.path.exists(datapath): os.makedirs(datapath)

import time
import calendar
from flask import Flask, render_template, request,send_from_directory
import json
import pandas as pd
import wikipedia
from utils.download_manager import DownloadManager
from utils.options import Options
from utils.cutter import Cutter
from utils.embedder import Embedder
from utils.sim_calculator import SimCalculator
from utils.res import Res
from threading import Thread
import threading
import warnings
res_ope = Res()
from time import sleep
_debug_mode = False  # True: only for offline tests.
_embed_method = 'labse'
_sc_method = 'faiss'

app = Flask(__name__)
dm = DownloadManager(_debug_mode)
cutter = Cutter()
embedder = Embedder()
data_path_bin = os.path.join(BASE_DIR, 'bin')

@app.route('/')
def home():
    return render_template('index.html')


def result_success(state=True, res=None, message="获取成功"):
    param = {
        'result': res,
        'message': message,
        'success': state,
        "timeStamp": calendar.timegm(time.gmtime())
    }
    return param, 200


def download_one_text(keyword: 'str', wiki_title: 'str',
                      language_code: 'str') -> 'str':
    """
    Return
    ------
    document_filepath :
        Downloaded TXT file path.
    """
    document = dm.download_text(title=wiki_title, language_code=language_code)
    document_filepath = dm.save_text(text=document,
                                     title=keyword,
                                     language_code=language_code)
    # Documents of one keyword in different languages have different names, which is not easy to retrieve.
    # So, here we use keyword, instead of wiki_title, to name every downloaded document.
    return document_filepath


def cut_one_text(document_filepath: 'str') -> 'str':
    """
    Parameters
    ----------
    document_filepath :
        The filepath of the document to be segmented.

    Return
    ------
    seg_filepath : str
        Segmented TXT file path.
    """
    with open(document_filepath, encoding='utf-8') as f:
        document = f.read()

    wiki_title, language_code = (document_filepath.strip('.txt').split('_'))
    seg_filepath = os.path.join(datapath,
                                f'{wiki_title}_{language_code}_seg.txt')

    with open(seg_filepath, 'w', encoding='utf-8') as f:
        for sentence in cutter.segmentation_auto(document, language_code):
            f.write(sentence)

    return seg_filepath



@app.route("/api/get_keyword_options", methods=["GET", "POST"])
def get_keyword_options(query=''):
    """
    Parameters
    ----------
    query :
        A fuzzy-lookup word.

    Return
    ------
    keyword_options : list[str<keyword option>]

    Example
    -------
    # >>> r = get_keyword_options(query='steve')
    # >>> print(r['res']['keyword_options'])
    ['Steve Jobs', 'STEVE', 'Steve Curry']
    """
    query = request.json
    if len(query['query']) > 0:
        keyword_options = wikipedia.search(query=query['query'], results=20)
        # TODO: expand this search function to more languages.
        # For more information about wikipedia.search(), please refer to the wikipedia documentation: https://wikipedia.readthedocs.io/en/latest/code.html#api
        res = {'keyword_options': keyword_options}
        return result_success(res=res)
    else:
        return result_success(res={'keyword_options': []})


@app.route("/api/get_wiki_title_options", methods=["GET", "POST"])
def get_wiki_title_options(keyword='str'):
    """
    Return
    ------
    options[i][0]: str, language code
    options[i][1]: str, Wiki title
    (only if debug_mode == True) options[i][2]: str, URL to the Wiki page

    Example
    -------
    # >>> _debug_mode = False
    # >>> r = get_wiki_title_options(keyword='Steve Jobs')
    # >>> print(r['res']['wiki_title_options'])
    [('en', 'Steve Jobs'), ('ace', 'Steve Jobs'), ('zh', '史蒂夫·乔布斯')]
    """
    query = request.json
    if len(query['keyword']) > 0:
        options = dm.get_langcode_title_options(keyword=query['keyword'])
        res = {'wiki_title_options': options}
        return result_success(res=res)
    else:
        return result_success(res={'wiki_title_options': []})



# BUTTON: Submit
@app.route("/api/analyze", methods=["GET", "POST"])
def analyze(keyword='', language_code1='', wiki_title1='', language_code2='', wiki_title2=''):
    query = request.json
    keyword = query['keyword']
    language_code1 = query['language_code1']
    wiki_title1 = query['wiki_title1']
    language_code2 = query['language_code2']
    wiki_title2 = query['wiki_title2']
    data_path = os.path.join(BASE_DIR, 'data')
    file_name = '''%s\\%s_%s_%s_res.json''' % (data_path, keyword, language_code1, language_code2)
    file_json = '''%s\\%s_%s_%s.json''' % (data_path, keyword, language_code1, language_code2)

    my_res = {'keyword': keyword, 'language_code1': language_code1, 'wiki_title1': wiki_title1,
              'language_code2': language_code2, 'wiki_title2': wiki_title2}
    if os.path.exists(file_name):
        with open(file_name, 'r') as rf:
            data = json.load(rf)
            return result_success(res=data)
    elif os.path.exists(file_json):
        res_ope.res_info(keyword=keyword, language_code1=language_code1, wiki_title1=wiki_title1, language_code2=language_code2, wiki_title2=wiki_title2)
        with open(file_name, 'r') as rf:
            data = json.load(rf)
            return result_success(res=data)
    else:
        if isexist(my_res):
            writefilecontent(my_res)
            if((getfileLength()<2 or len(threading.enumerate())<3)):
                thread = Thread(target=analyze2, kwargs={'keyword': keyword,'language_code1': language_code1,'wiki_title1' :wiki_title1,'language_code2' :language_code2,'wiki_title2' :wiki_title2})
                thread.start()
        return result_success(state=False,res=query, message="Query information has been added to the queue. Please query again in half an hour")




### 执行队列 start

##继续执行
def continuerun():
    time.sleep(15)
    if(getfileLength()>=1):
        print(threading.enumerate(),'线程列表',len(threading.enumerate()))
        with open(data_path_bin+'//threading.json', encoding='utf-8') as a:
            result = json.load(a)
            target=result[0]
            thread = Thread(target=analyze2, kwargs=target)
            thread.start()
            delfilecontent(target,False)

## 完成后删除记录
def delfilecontent(target,reload=True):
    result=[]
    with open(data_path_bin+'//threading.json', encoding='utf-8') as a:
        result = json.load(a)
        for i in result:
            if (i == target):
                print('删除前',result)
                result.remove(i)
                print('删除后', result)
    with open('threading.json', 'w', encoding='utf-8') as file_object:
        json.dump(result, file_object)
    if(reload):
        continuerun()

##判断是否有记录
def isexist(params):
    with open(data_path_bin+'//threading.json', mode='r+', encoding='utf-8') as file_object:
        result = json.load(file_object)
        if params in result:
            return False
        else:
            return True


## 获取文件长度
def getfileLength():
    with open(data_path_bin+'//threading.json', encoding='utf-8') as a:
        result = json.load(a)
    return len(result)
## 写入记录
def writefilecontent(obj):
    result = []
    print()
    with open(data_path_bin+'//threading.json', mode='r+', encoding='utf-8') as file_object:
        result = json.load(file_object)
    with open(data_path_bin+'//threading.json', 'w', encoding='utf-8') as file_object2:
        result.append(obj)
        json.dump(removeduplicate(result), file_object2)
### 去重
def removeduplicate(list1):
    """
    列表套字典去重复
    :param list1: 输入一个有重复值的列表
    :return: 返回一个去掉重复的列表
    """
    newlist = []
    for i in list1:  # 先遍历原始字典
        flag = True
        if newlist == []:  # 如果是空的列表就不会有重复，直接往里添加
            pass
        else:
            for j in newlist:
                count = len(i.keys())
                su = 0
                for key in i.keys():
                    if i[key]  == j[key]:
                        su += 1
                if su == count:
                    flag = False
        if flag:
            newlist.append(i)
    return newlist

### 执行队列 end




    #BUTTON: Submit
def analyze2(keyword: 'str' = 'Steve Jobs',
            language_code1: 'str' = 'en',
            wiki_title1: 'str' = 'Steve Jobs',
            language_code2: 'str' = 'zh',
            wiki_title2: 'str' = '史蒂夫·乔布斯',
            perspective: 'int' = 0):
    """Download article from Wiki, cut sentence, sentence embed, and calculate similarity.

    Return
    ------
    json_path : str
        The path to the JSON file. The file's format is like:
        list[dict['id_{language_code1}': int<id1>, 'id_{language_code2}': int<id2>, 'sim': float<similarity>]]
    """
    seg_text1_path = cut_one_text(
        download_one_text(keyword, wiki_title1, language_code1))
    seg_text2_path = cut_one_text(
        download_one_text(keyword, wiki_title2, language_code2))

    with open(seg_text1_path, 'r', encoding='utf-8') as f:
        seg_text1 = f.readlines()

    with open(seg_text2_path, 'r', encoding='utf-8') as f:
        seg_text2 = f.readlines()

    #NOTE: here we MUST use readlines() to get a list of strings.

    embedding1, embedding2 = embedder.embed_auto(seg_text1,
                                                 seg_text2,
                                                 method=_embed_method)
    #TODO: User can choose similarity's perspective.
    sc = SimCalculator(embedding1, embedding2)
    json_list = []
    json_path = os.path.join(
        datapath, f'{keyword}_{language_code1}_{language_code2}.json')

    #TODO: File's format and filename will change according to similarity perspective.
    for eb1_idx, eb2_idx, similarity in sc.sim_auto(method=_sc_method,
                                                    perspective=perspective):
        json_list.append({
            f'id_{language_code1}': int(eb1_idx),
            f'id_{language_code2}': int(eb2_idx),
            f'sim': float(similarity)
        })

    with open(json_path, 'w') as jsonfile:
        json.dump(json_list, jsonfile)
    #TODO: the method above load all data to a list. Try ways that save memory.
    print('Analyse finished!')
    warnings.simplefilter('ignore', ResourceWarning)
    delfilecontent({'keyword': keyword,'language_code1': language_code1,'wiki_title1' :wiki_title1,'language_code2' :language_code2,'wiki_title2' :wiki_title2})
    # res = {'json_path': json_path}
    # return result_success(res=res)


#BUTTON: Export
@app.route("/api/export_to_excel", methods=["GET", "POST"])
def export_to_excel():
    """
    Return
    ------
    excel_path : str
        Path to the exported XLSX file.
    """


    keyword = request.args.get("keyword")
    language1 = request.args.get("language1")
    language2 = request.args.get("language2")


    document1_filepath = os.path.join(datapath,
                                      f'{keyword}_{language1}_seg.txt')
    document2_filepath = os.path.join(datapath,
                                      f'{keyword}_{language2}_seg.txt')

    json_path = os.path.join(datapath,
                             f'{keyword}_{language1}_{language2}.json')

    with open(document1_filepath, 'r', encoding='utf-8') as doc1:
        doc1_list = doc1.readlines()

    with open(document2_filepath, 'r', encoding='utf-8') as doc2:
        doc2_list = doc2.readlines()

    with open(json_path, 'r') as f:
        json_list = json.load(f)

    df = pd.DataFrame(columns=[
        f'id_{language1}', language1, f'id_{language2}', language2, 'sim'
    ])

    for row_idx in range(len(json_list)):
        df.loc[row_idx] = [
            json_list[row_idx][f'id_{language1}'],
            doc1_list[json_list[row_idx][f'id_{language1}']],
            json_list[row_idx][f'id_{language2}'],
            doc2_list[json_list[row_idx][f'id_{language2}']],
            json_list[row_idx]['sim']
        ]

    excel_path = os.path.join(datapath,
                              f'{keyword}_{language1}_{language2}.xlsx')
    df.to_excel(excel_path, encoding='utf-8-sig', index=False)
    res = {'excel_path': excel_path}

    return send_from_directory(datapath,f'{keyword}_{language1}_{language2}.xlsx')


#TODO: Apply generator on the document/sentence passing between steps.
if __name__ == '__main__':
    app.run()