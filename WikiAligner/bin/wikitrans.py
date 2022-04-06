import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.
sys.path.append(BASE_DIR)
datapath = os.path.join(BASE_DIR, 'data')

import wikipedia
from utils.download_manager import DownloadManager
from utils.options import Options
from utils.cut import Cut
from utils.embedder import Embedder
from utils.aligners import Aligners
from collections import OrderedDict
from flask import Flask
import json

app = Flask(__name__)
# from utils import embedder, aligners, json_formatter

_debug_mode = True
_prompt_query = '=' * 5 + 'The keyword you\'d like to search: ' + '=' * 5
_prompt_related_queries = '=' * 5 + 'Related keywords from Wiki' + '=' * 5
_prompt_select_query = 'Please select: '
_prompt_wiki_title_options = '=' * 5 + 'Available language codes and their Wiki titles' + '=' * 5
_prompt_select_wiki_title = 'Please select: '
_prompt_select_main_menu = 'Press the key to select from the menu: '

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


@app.route('/download_one_text')
def download_one_text():
    query_options = wikipedia.search(query=dm.get_query(_prompt_query),
                                     results=20)
    #TODO: expand this search function to more languages.
    # For more information about wikipedia.search(), please refer to the wikipedia documentation: https://wikipedia.readthedocs.io/en/latest/code.html#api
    print_options(query_options, _prompt_related_queries)
    keyword = get_option_choice(query_options, _prompt_select_query)

    wiki_title_options = dm.get_langcode_title_options(keyword)
    print_options(wiki_title_options, _prompt_wiki_title_options)
    if _debug_mode == False:
        language_code, wiki_title = get_option_choice(
            wiki_title_options, _prompt_select_wiki_title)
    else:
        language_code, wiki_title, wiki_link = get_option_choice(
            wiki_title_options, _prompt_select_wiki_title)

    document = dm.download_text(title=wiki_title, languageCode=language_code)
    document_filepath = dm.save_text(text=document,
                                     wiki_title=keyword,
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


def download_and_cut():
    raw_document_filepath = download_one_text()
    cut_one_text(raw_document_filepath)


def embed(document_filepath):
    with open(document_filepath, 'r', encoding='utf-8') as f:
        document = f.readlines()
        #NOTE: here we MUST use readlines().
        # f.read() return a single string, while f.readlines() return a list of strings.
    # model = embedder.load_labse()

    return embedder.embed_with_labse(document)


def embed_and_align():
    """
    Return
    ------
    tuple[<embedding1's index>, <embedding2's index>, <similarity>]
    """
    wiki_title = input('Wiki title: ')
    language1 = input('Language 1: ')
    language2 = input('Language 2: ')
    document1_filepath = os.path.join(datapath,
                                      f'{wiki_title}_{language1}_seg.txt')
    document2_filepath = os.path.join(datapath,
                                      f'{wiki_title}_{language2}_seg.txt')
    # embedding1 = embed(document1_filepath)
    # embedding2 = embed(document2_filepath)
    aligner = Aligners(embed(document1_filepath), embed(document2_filepath))
    json_path = os.path.join(datapath,
                             f'{wiki_title}_{language1}_{language2}.json')
    with open(json_path, 'w') as jsonfile:
        for eb1_idx, eb2_idx, similarity in aligner.align_auto(method='faiss'):
            json.dump(
                [int(eb1_idx), int(eb2_idx),
                 float(similarity)], jsonfile)

    # return ((int(eb1_idx), int(eb2_idx), similarity)
    #         for eb1_idx, eb2_idx, similarity in aligner.align_with_faiss(
    #             embedding1, embedding2))

    # for row_idx, max_col_idx, item in aligner.align_auto(method='faiss'):
    #     print(f'{row_idx}---{max_col_idx}---{item}')


# @app.route('/main')
def loop():
    #TODO: one wiki title, select language for two times.
    menu = [
        Options('Download and cut', download_and_cut),
        Options('Embed and align', embed_and_align),
        Options('Quit', sys.exit)
    ]
    print_options(menu, '')
    menu_option = get_option_choice(menu, _prompt_select_main_menu)
    menu_option.choose()
    _ = input('Press ENTER to repeat')


#TODO: Apply generator on the document/sentence passing between steps.
if __name__ == '__main__':
    while True:
        loop()