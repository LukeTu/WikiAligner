import os
import requests
import wikipedia

#TODO: change all URLs and parameters to the api to CAPITAL and save them in setting.py

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR: WikiTrans base directory.


class DownloadManager:
    def __init__(self, debug_mode=False) -> None:
        self.data_path = os.path.join(BASE_DIR, 'data')

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        self.debug_mode = debug_mode

    def get_query(self, prompt):
        if prompt:
            print(prompt)
        query = input() or None
        return query

    def get_langcode_title_options(
            self,
            keyword: str = '',
            append_links=False) -> 'list[tuple[str,str,str]]':
        """Search and return available (language code, Wiki title, link) options.

        : append_links : if user want to return the URL of the Wiki page.

        Return :
        options[i][0]: language code
        options[i][1]: Wiki title
        options[i][2]: URL to the Wiki page (only if append_links == True)

        This function has refered 'MediaWiki API help' -> 'action'='query' -> 'prop'='langlinks' @https://www.mediawiki.org/w/api.php?action=help&modules=query%2Blanglinks
        """
        endpoint = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "langlinks",
            "lllimit": "max",
            "titles": keyword,
            "format": "json",
            "llurl": True  # Get link to the Wiki page. 
        }
        jsonText = requests.Session().get(url=endpoint, params=params).json()

        if self.debug_mode: append_links = True

        if not append_links:
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
        return options

    def download_text(self,
                      title: str = '',
                      language_code: str = 'en') -> 'str':
        """Download the wiki content of the target title and langcode.
        return: str, the content(raw text).
        For more on the api @https://www.mediawiki.org/w/api.php?action=help&modules=main
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
        jsonText = requests.Session().get(url=url, params=params).json()
        return jsonText['query']['pages'][0]['extract']

    def save_text(self, text: str, title: str, language_code: str) -> None:
        filepath = os.path.join(self.data_path, f'{title}_{language_code}.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(text)
        print(f'Text saved at {filepath}')
        return filepath