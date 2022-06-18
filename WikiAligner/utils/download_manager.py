import os
from typing import Union
import requests
from polyglot.text import Text
from polyglot.detect.base import logger as polyglot_logger

polyglot_logger.setLevel("ERROR")  # Close the warning from polyglot.

import _global


class DownloadManager:
    def __init__(self, save_path, debug_mode=False) -> None:
        self.save_path = save_path
        self.debug_mode = debug_mode
        return None

    def get_query(self, prompt: 'str' = ''):
        if prompt:
            print(prompt)
        query = input() or None
        return query

    def _identify_lang(self, text):
        return Text(text).language.code

    def search_keyword(self, query, limit=10):
        langcode = self._identify_lang(query)
        endpoint = f"https://{langcode}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": ""
        }
        json_text = requests.Session().get(url=endpoint, params=params).json()
        keywords = [_['title'] for _ in json_text['query']['search']]
        return keywords

    def get_langcode_title_options(
        self,
        keyword: 'str' = '',
    ) -> Union['list[tuple[str, str]]', 'list[tuple[str, str, str]]']:
        """Search and return available (language code, Wiki title, link) options.

        Parameters
        ----------
        keyword :
            A valid Wiki keyword in English. Note that it's different from Wiki title, 
            which should be in the target language. As shown in the example below, 
            "Steve Jobs" is a valid wiki keyword, and "史蒂夫·乔布斯" is a Wiki title in Chinese.

        Return
        ------
        options[i][0] : str
            Language code in ISO 639-1 (It can be tested using France: 639-1=fr, 639-2=fre/fra, 639-3=fra)
        options[i][1] : str
            Wiki title
        (only if debug_mode == True) options[i][2] : str 
            URL to the Wiki page

        For more information, please refer to 'MediaWiki API help' 
        -> 'action'='query' -> 'prop'='langlinks' 
        -> https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks

        Example
        -------
        >>> debug_mode = False
        >>> dm = DownloadManager(debug_mode)
        >>> result = dm.get_langcode_title_options(keyword='Steve Jobs')
        >>> print(result)
        [('en', 'Steve Jobs'), ('ace', 'Steve Jobs'), ('zh', '史蒂夫·乔布斯')]  
        """
        langcode = self._identify_lang(keyword)
        #TODO: 真的需要把keyword变成不同语言吗？这样就违反了keyword的英语一致性？
        endpoint = f"https://{langcode}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "langlinks",
            "lllimit": "max",
            "titles": keyword,
            "format": "json",
            "llurl": True  # Get link to the Wiki page. 
        }
        jsonText = requests.Session().get(url=endpoint, params=params).json()

        # Append links only in debug-mode.
        if not self.debug_mode:
            options = [(lang_dict['lang'], lang_dict['*'])
                       for lang_dict in list(
                           jsonText['query']['pages'].values())[0]['langlinks']
                       ]
            eng_option = (
                'en',
                keyword,
            )

        else:
            options = [(lang_dict['lang'], lang_dict['*'], lang_dict['url'])
                       for lang_dict in list(
                           jsonText['query']['pages'].values())[0]['langlinks']
                       ]
            eng_option = (
                'en', keyword,
                f'https://en.wikipedia.org/wiki/{keyword.replace(" ","_")}')
            # lang_dict['lang']: language code
            # lang_dict['*']: Wiki title
            # lang_dict['url']: URL to the Wiki page

        # The <endpoint> above doesn't return 'en'(English) option, so we have to insert it additionally.
        options.insert(0, eng_option)
        return sorted(options, key=lambda option: option[0])

    def filter_option(
        self, options, languages: 'list'
    ) -> Union['list[tuple[str, str]]', 'list[tuple[str, str, str]]']:
        """Filter and keep options only within a language list user specifies.

        Parameters
        ----------
        options :
            Language code and Wiki title options.
        languages :
            Language code of languages user would like to keep.
        
        Return
        ------
        options_ :
            Filtered option; the same format as <options>.
        """
        languages = sorted(languages)
        #NOTE: <options> returned from self.get_langcode_title_options() is already sorted by the language code.
        i = 0
        j = 0
        options_ = []

        while i < len(languages) and j < len(options):
            if languages[i] == options[j][0]:
                options_.append(options[j])
                i += 1
                j += 1
            elif languages[i] > options[j][0]:
                j += 1
            else:
                i += 1

        return options_

    def download_text(self,
                      title: 'str' = '',
                      language_code: 'str' = 'en') -> 'str':
        """Download the wiki content of the target title and langcode.
        
        Return
        ------
        str, the content(raw text).
        
        For more about the api @https://www.mediawiki.org/w/api.php?action=help&modules=main
        """
        # url = f'https://{languageCode}.wikipedia.org/w/api.php?action=query&prop=extracts&exlimit=1&utf8=1&titles={title}&explaintext=1&formatversion=2&format=json'
        #TODO: parse api (action)
        #TODO: where is simplified Chinese? 可能 wiki_title是史蒂夫·賈伯斯，而非史蒂夫·乔布斯。两者url其余部分一致。
        #并不是，本身是简体的。zh ⋅⋅⋅⋅ 史蒂夫·乔布斯 ⋅⋅⋅⋅ https://zh.wikipedia.org/wiki/%E5%8F%B2%E8%92%82%E5%A4%AB%C2%B7%E4%B9%94%E5%B8%83%E6%96%AF
        # 可能是api的问题？api是否会默认设置地区？
        url = f'https://{language_code}.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'prop': 'extracts',
            'exlimit': '1',
            'utf8': '1',
            'titles': title,
            'explaintext': '1',
            'formatversion': '2',
            'format': 'json'
        }
        json_text = requests.Session().get(url=url, params=params).json()
        return json_text['query']['pages'][0]['extract']

    def save_text(self, text: 'str', title: 'str',
                  language_code: 'str') -> None:
        """Save downloaded text.
        """
        filepath = os.path.join(self.save_path, f'{title}_{language_code}.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(text)
        print(f'Text saved at {filepath}')
        return filepath


if __name__ == '__main__':
    # Tests
    dm = DownloadManager(_global.CUTSPATH, debug_mode=False)

    ####################################################################
    # Test self.search_keyword()
    q = 'steve jobs'
    print(dm.search_keyword(q))
    # keyword = 'Steve Jobs'

    ####################################################################
    # Test self.get_langcode_title_options()
    # options = dm.get_langcode_title_options(keyword=keyword)
    # print(f'Options of {keyword}: \n', sorted(languages))

    ####################################################################
    # Test language filter
    # with open(os.path.join(_global.BASE_DIR, 'utils',
    #                        'labse_languages.txt')) as f:
    #     languages = f.readlines()
    #     languages = [l.strip() for l in languages]

    # print('LaBSE languages:\n', sorted(languages))
    # filtered = dm.filter_option(options, languages)
    # print(f'Options filtered:\n', filtered)