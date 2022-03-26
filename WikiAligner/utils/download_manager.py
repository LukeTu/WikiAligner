import requests
import wikipedia


class DownloadManager:
    def __init__(self) -> None:
        pass

    def get_query(self):
        print('=' * 5, 'The keyword you\'d like to search:', '=' * 5)
        query = input() or None
        return query

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

########################

    def print_options(self, options, prompt):
        """Print options as (<index>)......<option>
        """
        if prompt:
            print(prompt)
        for idx, option in enumerate(options):
            print(f'({idx + 1})......{option}')

    def print_keyword_options(self, options):
        for idx, kw in enumerate(options):
            print(idx + 1, kw)

    def print_options2(self, options) -> None:
        """
        options[i][0]: language code
        options[i][1]: Wiki title
        options[i][2]: URL to the Wiki page
        """
        print('=' * 5, "Available language codes and their Wiki titles",
              '=' * 5)
        for idx, option in enumerate(options):
            print(f'{idx+1}.{option[0]}    {option[1]}')

#########################

    def get_option_choice(self, options, prompt: str = ''):
        if prompt:
            print(prompt)
        option_idx = int(input()) - 1
        return options[option_idx]

    def get_keyword_option(self, options) -> str:
        kw_idx = int(
            input(
                "Choose the index of your Wiki keyword from those related ones:"
            )) - 1
        keyword = options[kw_idx]
        return keyword

    def get_option_choice2(self, options) -> 'tuple[str, str, str]':
        """
        options[i][0]: language code
        options[i][1]: Wiki title
        options[i][2]: URL to the Wiki page
        """
        print('=' * 5, "Your choice: ", '=' * 5)
        idx = int(input()) - 1
        return options[idx]


#############################

    def download_text(self,
                      title: str = '',
                      languageCode: str = 'en') -> 'str':
        """Download the wiki content of the target title and langcode.
        return: str, the content(raw text).
        For more on the api @https://www.mediawiki.org/w/api.php?action=help&modules=main
        """
        # url = f'https://{languageCode}.wikipedia.org/w/api.php?action=query&prop=extracts&exlimit=1&utf8=1&titles={title}&explaintext=1&formatversion=2&format=json'
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