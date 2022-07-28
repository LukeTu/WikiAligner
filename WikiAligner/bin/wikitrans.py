#TODO: check all paths, if not exists, create automatically.
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # BASE_DIR: WikiTrans base directory.
sys.path.append(BASE_DIR)
_debug_mode = False  # True: only for offline tests.
_embed_method = 'labse'  # Sentence embedding model.
_sc_method = 'faiss'  # Simularity calculation method.

import time
from threading import Thread
import calendar
from flask import Flask, render_template, request
import json
import pandas as pd
import numpy as np
import wikipedia
from utils import _global
from utils.download_manager import DownloadManager
from utils.cutter import Cutter
from utils.embedder import Embedder
from utils.sim_calculator import SimCalculator
# from utils.res import Res

app = Flask(__name__)
dm = DownloadManager(_global.CUTSPATH, _debug_mode)
cutter = Cutter()
embedder = Embedder()


@app.route('/')
def home():
    return render_template('index.html')


# BUTTON: Submit
#TODO: check if downloaded text empty. How to embed it?
# Return: <Oops! Wikipedia does not provide the term in this language.>
def analyze(keyword: 'str' = None,
            language_code1: 'str' = None,
            wiki_title1: 'str' = None,
            language_code2: 'str' = None,
            wiki_title2: 'str' = None,
            perspective: 'int' = 0):

    # Read frontend query.
    if keyword == None:
        # If <keyword> has not been fetched, other variables should be empty as well,
        # so we only have to check <keyword>.
        query = request.json
        keyword = query['keyword']
        language_code1 = query['language_code1']
        wiki_title1 = query['wiki_title1']
        language_code2 = query['language_code2']
        wiki_title2 = query['wiki_title2']

    embed1_path = os.path.join(_global.EMBEDPATH,
                               f'{keyword}_{language_code1}')
    embed2_path = os.path.join(_global.EMBEDPATH,
                               f'{keyword}_{language_code2}')

    # If a doc's embedding exists already, do not calculate again.
    if not os.path.exists(embed1_path) and not os.path.exists(embed2_path):
        seg_text1_path = cut_one_text(
            download_one_text(keyword, wiki_title1, language_code1))
        seg_text2_path = cut_one_text(
            download_one_text(keyword, wiki_title2, language_code2))

        with open(seg_text1_path, 'r', encoding='utf-8') as f:
            seg_text1 = f.readlines()

        with open(seg_text2_path, 'r', encoding='utf-8') as f:
            seg_text2 = f.readlines()

        #NOTE: here we MUST use readlines() to get a list of strings.

        embed1, embed2 = embedder.embed_both(seg_text1,
                                             seg_text2,
                                             method=_embed_method)
        embedder.save(embed1, embed2, f'{keyword}_{language_code1}',
                      f'{keyword}_{language_code2}')
    elif not os.path.exists(embed1_path) and os.path.exists(embed2_path):
        seg_text1_path = cut_one_text(
            download_one_text(keyword, wiki_title1, language_code1))

        with open(seg_text1_path, 'r', encoding='utf-8') as f:
            seg_text1 = f.readlines()

        embed1 = embedder.embed_single(seg_text1, method=_embed_method)
        embed2 = np.load(embed2_path)
    elif os.path.exists(embed1_path) and not os.path.exists(embed2_path):
        embed1 = np.load(embed1_path)
    else:
        embed1 = np.load(embed1_path)
        embed2 = np.load(embed2_path)

    sc = SimCalculator(embed1, embed2)
    json_list = []
    json_path = os.path.join(
        _global.SIMPATH, f'{keyword}_{language_code1}_{language_code2}.json')

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
    res = {'json_path': json_path}
    return result_success(res=res)


# Old version
# @app.route("/api/analyze", methods=["GET", "POST"])
# def analyze(keyword: 'str', language_code1: 'str', wiki_title1: 'str',
#             language_code2: 'str', wiki_title2: 'str', perspective: 'int'):
#     """Download article from Wiki, cut sentence, sentence embed, and calculate similarity.

#     Return
#     ------
#     json_path : str
#         The path to the JSON file. The file's format is like:
#         list[dict['id_{language_code1}': int<id1>, 'id_{language_code2}': int<id2>, 'sim': float<similarity>]]
#     """
#     seg_text1_path = cut_one_text(
#         download_one_text(keyword, wiki_title1, language_code1))
#     seg_text2_path = cut_one_text(
#         download_one_text(keyword, wiki_title2, language_code2))

#     with open(seg_text1_path, 'r', encoding='utf-8') as f:
#         seg_text1 = f.readlines()

#     with open(seg_text2_path, 'r', encoding='utf-8') as f:
#         seg_text2 = f.readlines()

#     #NOTE: here we MUST use readlines() to get a list of strings.

#     embedding1, embedding2 = embedder.embed_auto(seg_text1,
#                                                  seg_text2,
#                                                  method=_embed_method)
#     #TODO: User can choose similarity's perspective.
#     sc = SimCalculator(embedding1, embedding2)
#     json_list = []
#     json_path = os.path.join(
#         datapath, f'{keyword}_{language_code1}_{language_code2}.json')

#     #TODO: File's format and filename will change according to similarity perspective.
#     for eb1_idx, eb2_idx, similarity in sc.sim_auto(method=_sc_method,
#                                                     perspective=perspective):
#         json_list.append({
#             f'id_{language_code1}': int(eb1_idx),
#             f'id_{language_code2}': int(eb2_idx),
#             f'sim': float(similarity)
#         })

#     with open(json_path, 'w') as jsonfile:
#         json.dump(json_list, jsonfile)
#     #TODO: the method above load all data to a list. Try ways that save memory.
#     print('Analyse finished!')
#     res = {'json_path': json_path}
#     return result_success(res=res)


def download_and_embed_one(
    keyword: 'str' = None,
    language_code: 'str' = None,
    wiki_title: 'str' = None,
):
    """Download, sentence segmentation and sentence embedding.
    """

    seg_path = cut_one_text(
        download_one_text(keyword, wiki_title, language_code))

    #TODO: rid this step to read from drive.
    with open(seg_path, 'r', encoding='utf-8') as f:
        seg_text = f.readlines()
    #NOTE: here we MUST use readlines() to get a list of strings.

    embed1, embed2 = embedder.embed_single(seg_text, method=_embed_method)
    embedder.save(embed1, embed2, f'{keyword}_{language_code1}',
                  f'{keyword}_{language_code2}')
    return embed1, embed2


def download_and_embed_both(keyword: 'str' = None,
                            language_code1: 'str' = None,
                            wiki_title1: 'str' = None,
                            language_code2: 'str' = None,
                            wiki_title2: 'str' = None):
    """Download, sentence segmentation and sentence embedding.
    """
    if keyword == None:
        # If <keyword> has not been fetched, other variables should be empty as well,
        # so we only have to check <keyword>.
        query = request.json
        keyword = query['keyword']
        language_code1 = query['language_code1']
        wiki_title1 = query['wiki_title1']
        language_code2 = query['language_code2']
        wiki_title2 = query['wiki_title2']

    seg_text1_path = cut_one_text(
        download_one_text(keyword, wiki_title1, language_code1))
    seg_text2_path = cut_one_text(
        download_one_text(keyword, wiki_title2, language_code2))

    #TODO: rid this step to read from drive.
    with open(seg_text1_path, 'r', encoding='utf-8') as f:
        seg_text1 = f.readlines()

    with open(seg_text2_path, 'r', encoding='utf-8') as f:
        seg_text2 = f.readlines()

    #NOTE: here we MUST use readlines() to get a list of strings.

    embed1, embed2 = embedder.embed_both(seg_text1,
                                         seg_text2,
                                         method=_embed_method)
    embedder.save(embed1, embed2, f'{keyword}_{language_code1}',
                  f'{keyword}_{language_code2}')
    return embed1, embed2


#BUTTON: Export
@app.route("/api/export_to_excel", methods=["GET", "POST"])
def export_to_excel(keyword: 'str', language1: 'str', language2: 'str'):
    """
    Return
    ------
    excel_path : str
        Path to the exported XLSX file.
    """
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
    return result_success(res=res)


#BOX:
@app.route("/api/get_keyword_options", methods=["GET", "POST"])
def get_keyword_options(user_query: 'str' = None):
    """
    Parameters
    ----------
    query :
        A fuzzy-lookup word.

    Return
    ------
    keyword_options : list[str<keyword>]

    Example
    -------
    # >>> r = get_keyword_options(query='steve')
    # >>> print(r['res']['keyword_options'])
    # ['Steve Jobs', 'STEVE', 'Steve Curry']
    """
    if user_query == None:
        query = request.json
        user_query = query['query']

    if len(user_query) > 0:
        keyword_options = wikipedia.search(query=user_query, results=20)
        # TODO: expand this search function to more languages.
        # For more information about wikipedia.search(), please refer to the wikipedia documentation: https://wikipedia.readthedocs.io/en/latest/code.html#api
        res = {'keyword_options': keyword_options}
        return result_success(res=res)
    else:
        return result_success(res={'keyword_options': []})


#SELECTION LIST
@app.route("/api/get_wiki_title_options", methods=["GET", "POST"])
def get_wiki_title_options(keyword: 'str' = None):
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
    # [('en', 'Steve Jobs'), ('ace', 'Steve Jobs'), ('zh', '史蒂夫·乔布斯')]
    """
    if keyword == None:
        query = request.json
        keyword = query['keyword']

    if len(keyword) > 0:
        options = dm.get_langcode_title_options(keyword=keyword)
        res = {'wiki_title_options': options}
        return result_success(res=res)
    else:
        return result_success(res={'wiki_title_options': []})


def result_success(state=True, res=None, message="获取成功"):
    param = {
        'result': res,
        'message': message,
        'success': state,
        "timeStamp": calendar.timegm(time.gmtime())
    }
    return param, 200


#TODO: when using labse, constrain language options.
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
    seg_filepath = os.path.join(_global.CUTSPATH,
                                f'{wiki_title}_{language_code}_seg.txt')

    with open(seg_filepath, 'w', encoding='utf-8') as f:
        for sentence in cutter.segmentation_auto(document, language_code):
            f.write(sentence)

    return seg_filepath

    file_name = '''%s\\%s_%s_%s_res.json''' % (datapath, keyword,
                                               language_code1, language_code2)
    if os.path.exists(file_name):
        with open(file_name, 'r') as rf:
            data = json.load(rf)
            return result_success(res=data)
    else:
        thread = Thread(target=analyze2,
                        kwargs={
                            'keyword': keyword,
                            'language_code1': language_code1,
                            'wiki_title1': wiki_title1,
                            'language_code2': language_code2,
                            'wiki_title2': wiki_title2
                        })
        thread.start()
        return result_success(
            state=False,
            res=query,
            message=
            "Query information has been added to the queue. Please query again in half an hour"
        )


#TODO: Apply generator on the document/sentence passing between steps.
if __name__ == '__main__':
    app.run()
    # Test
    # analyze(keyword='Steve Jobs',
    #         language_code1='en',
    #         wiki_title1='Steve Jobs',
    #         language_code2='zh',
    #         wiki_title2='史蒂夫·乔布斯',
    #         perspective=0)
    # export_to_excel(keyword='Steve Jobs', language1='en', language2='zh')