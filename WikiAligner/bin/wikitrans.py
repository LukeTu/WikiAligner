#TODO: check all paths, if not exists, create automatically.
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.
sys.path.append(BASE_DIR)
datapath = os.path.join(BASE_DIR, 'data')
if not os.path.exists(datapath): os.makedirs(datapath)

from flask import Flask
import json
import pandas as pd
import wikipedia
from utils.download_manager import DownloadManager
from utils.options import Options
from utils.cut import Cut
from utils.embedder import Embedder
from utils.aligners import Aligners

_debug_mode = False  # True: only for offline tests.
_prompt_query = '=' * 5 + 'The keyword you\'d like to search: ' + '=' * 5
_prompt_related_queries = '=' * 5 + 'Related keywords from Wiki' + '=' * 5
_prompt_select_query = 'Please select: '
_prompt_wiki_title_options = '=' * 5 + 'Available language codes and their Wiki titles' + '=' * 5
_prompt_select_wiki_title = 'Please select: '
_prompt_select_main_menu = 'Press the key to select from the menu: '

app = Flask(__name__)
dm = DownloadManager(_debug_mode)
cutter = Cut()
embedder = Embedder()
# aligner = Aligners()


def print_options(options, prompt):
    """Print options as (<index>)......<option>
    """
    if prompt:
        print(prompt)

    for idx, option in enumerate(options):
        # If <option> itself has several sub-options, separate them with spaces.
        if isinstance(option, list) or isinstance(option, tuple):
            option_str = ' ⋅⋅⋅⋅ '.join(option)
            print(f'({idx + 1})    {option_str}')
            continue
        print(f'({idx + 1})    {option}')


def get_option_choice(options, prompt: str = ''):
    """Get option choice from user input. <option index> = <user input> - 1.
    """
    if prompt:
        print(prompt)

    option_idx = int(input()) - 1
    print('Option has been chosen successfully!')
    return options[option_idx]


def download_one_text(keyword, wiki_title, language_code) -> str:
    """
    Return
    ------
    Downloaded TXT file path.
    """
    document = dm.download_text(title=wiki_title, language_code=language_code)
    document_filepath = dm.save_text(text=document,
                                     title=keyword,
                                     language_code=language_code)
    # Documents of one keyword in different languages have different names, which is not easy to retrieve.
    # So, here we use keyword, instead of wiki_title, to name every downloaded document.
    return document_filepath


def cut_one_text(document_filepath, export=True):
    """
    Parameters
    ----------
    export: If export and save as a TXT file.
    """
    #TODO: only write to a TXT file when export == True; generate a sentence otherwise.
    with open(document_filepath, encoding='utf-8') as f:
        document = f.read()
    wiki_title, language_code = (document_filepath.strip('.txt').split('_'))
    seg_filepath = os.path.join(datapath,
                                f'{wiki_title}_{language_code}_seg.txt')
    with open(seg_filepath, 'w', encoding='utf-8') as f:
        if export:
            for sentence in cutter.segmentation_auto(document, language_code):
                f.write(sentence)
        # else:
        #     for sentence in cutter.segmentation_auto(document, language_code):
        #         yield sentence

        # if language_code in ['zh', 'zh-classical']:
        #     for sentence in cutter.segmentation_zh(document):
        #         f.write(sentence)
        # else:
        #     for sentence in cutter.segmentation_ie(document):
        #         f.write(sentence)


def embed(document_filepath):
    with open(document_filepath, 'r', encoding='utf-8') as f:
        document = f.readlines()
        #NOTE: here we MUST use readlines().
        # f.read() return a single string, while f.readlines() return a list of strings.
    # model = embedder.load_labse()

    return embedder.embed_with_labse(document)


@app.route("/api/search", methods=["GET", "POST"])
def search():
    query_options = wikipedia.search(query=dm.get_query(_prompt_query),
                                     results=20)
    #TODO: expand this search function to more languages.
    # For more information about wikipedia.search(), please refer to the wikipedia documentation: https://wikipedia.readthedocs.io/en/latest/code.html#api
    print_options(query_options, _prompt_related_queries)
    global KEYWORD
    KEYWORD = get_option_choice(query_options, _prompt_select_query)
    return KEYWORD


@app.route("/api/choose_wiki_title", methods=["GET", "POST"])
def choose_wiki_title(keyword):
    wiki_title_options = dm.get_langcode_title_options(keyword)
    print_options(wiki_title_options, _prompt_wiki_title_options)
    if _debug_mode == False:
        language_code, wiki_title = get_option_choice(
            wiki_title_options, _prompt_select_wiki_title)
        return language_code, wiki_title
    else:
        language_code, wiki_title, wiki_link = get_option_choice(
            wiki_title_options, _prompt_select_wiki_title)
        return language_code, wiki_title, wiki_link


#BUTTON: "Analyze" OR "Align"
@app.route("/api/analyze", methods=["GET", "POST"])
def analyze(keyword):
    language_code1, wiki_title1 = choose_wiki_title(keyword)
    language_code2, wiki_title2 = choose_wiki_title(keyword)
    #TODO: asynchronously embed text during choosing wiki title.
    embedding1 = embed(
        cut_one_text(download_one_text(keyword, wiki_title1, language_code1),
                     export=True))
    embedding2 = embed(
        cut_one_text(download_one_text(keyword, wiki_title2, language_code2),
                     export=True))
    aligner = Aligners(embedding1, embedding2)
    json_list = []
    json_path = os.path.join(
        datapath, f'{keyword}_{language_code1}_{language_code2}.json')

    for eb1_idx, eb2_idx, similarity in aligner.align_auto(method='faiss'):
        json_list.append({
            f'id_{language_code1}': int(eb1_idx),
            f'id_{language_code2}': int(eb2_idx),
            f'sim': float(similarity)
        })

    with open(json_path, 'w') as jsonfile:
        json.dump(json_list, jsonfile)
    #TODO: the method above load all data to a list. Try ways that save memory.
    return language_code1, language_code2, json_path
    # with open(json_path, 'w') as jsonfile:
    #     for eb1_idx, eb2_idx, similarity in aligner.align_auto(method='faiss'):
    #         json.dump(
    #             {
    #                 f'id_{language1}': int(eb1_idx),
    #                 f'id_{language2}': int(eb2_idx),
    #                 f'sim': float(similarity)
    #             }, jsonfile)

    # return ((int(eb1_idx), int(eb2_idx), similarity)
    #         for eb1_idx, eb2_idx, similarity in aligner.align_with_faiss(
    #             embedding1, embedding2))

    # for row_idx, max_col_idx, item in aligner.align_auto(method='faiss'):
    #     print(f'{row_idx}---{max_col_idx}---{item}')


#BUTTON: Export
@app.route("/api/export_to_excel", methods=["GET", "POST"])
def export_to_excel(keyword, language1, language2):
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


@app.route('/main')
def loop():
    menu = [Options('Search', search), Options('Quit', sys.exit)]
    print_options(menu, '')
    menu_option = get_option_choice(menu, _prompt_select_main_menu)
    menu_option.choose()
    _ = input('Press ENTER to repeat')


#TODO: Apply generator on the document/sentence passing between steps.
if __name__ == '__main__':
    while True:
        loop()