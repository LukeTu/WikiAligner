import requests
import wikipedia

#TODO: change all URLs and parameters to the api to CAPITAL and save them in setting.py


class DownloadManager:
    def __init__(self) -> None:
        pass

    def search_available_keyword_options(self, query: str = '') -> 'list[str]':
        """Search all Wiki titles related to the keyword, and let user determine which specific title.
        : query : the word for furry search in English.
        For more information, please refer to the wikipedia documentation: https://wikipedia.readthedocs.io/en/latest/code.html#api
        """
        #TODO: expand this function more languages.
        return wikipedia.search(query=query, results=20)

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

        if not append_links:
            options = [(lang_dict['lang'], lang_dict['*'])
                       for lang_dict in list(
                           jsonText['query']['pages'].values())[0]['langlinks']
                       ]
        else:
            options = [(lang_dict['lang'], lang_dict['*'], lang_dict['url'])
                       for lang_dict in list(
                           jsonText['query']['pages'].values())[0]['langlinks']
                       ]
        # lang_dict['lang']: language code
        # lang_dict['*']: Wiki title
        # lang_dict['url']: URL to the Wiki page

        # The endpoint above doesn't return 'en'(English) option, so we have to insert it additionally.
        eng_option = (
            'en', keyword,
            f'https://en.wikipedia.org/wiki/{keyword.replace(" ","_")}')
        options.insert(0, eng_option)
        return options

    def download_text(self,
                      title: str = '',
                      languageCode: str = 'en') -> 'str':
        """Download the wiki content of the target title and langcode.
        return: str, the content(raw text).
        For more on the api @https://www.mediawiki.org/w/api.php?action=help&modules=main
        """
        # url = f'https://{languageCode}.wikipedia.org/w/api.php?action=query&prop=extracts&exlimit=1&utf8=1&titles={title}&explaintext=1&formatversion=2&format=json'
        #TODO: parse api (action)
        url = f'https://{languageCode}.wikipedia.org/w/api.php'
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

    def save_text(self, text: str, wiki_title: str,
                  language_code: str) -> None:
        filepath = f'{wiki_title}_{language_code}.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(text)
        return f'Text saved at {filepath}'