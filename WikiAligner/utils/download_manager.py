import os
from typing import Union
import requests
from bs4 import BeautifulSoup
import fasttext
import re


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
        model_path = os.path.join(_global.MODEL_PATH, 'lid.176.ftz')
        model = fasttext.load_model(model_path)
        return model.predict(text, k=2)

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

    def download_oldid_text(self, langcode: 'str', oldid: 'str'):
        endpoint = f"https://{langcode}.wikipedia.org/w/api.php"
        params = {
            "action": "parse",
            "format": "json",
            "oldid": oldid,
            "prop": "text",
            "formatversion": "2"
        }
        json_text = requests.Session().get(url=endpoint, params=params).json()
        return json_text['parse']['text']

    def clean_oldid_text(self, text: 'str'):
        soup = BeautifulSoup(text)

        # Remove the table of content.
        try:
            soup.find('div', attrs={'class': 'toc'}).extract()
        except AttributeError:
            pass

        # Remove the table for brief info at the top right of a page.
        try:
            soup.find('table', attrs={
                'class': 'infobox biography vcard'
            }).extract()
        except AttributeError:
            pass

        try:
            soup.find('table', attrs={'class': 'infobox'}).extract()
        except AttributeError:
            pass

        # Remove the table for related items at the end of a page.
        try:
            soup.find('table', attrs={'class': 'navbox'}).extract()
        except AttributeError:
            pass

        try:
            for div in soup.find_all('div', attrs={'class': 'navbox'}):
                div.extract()
        except AttributeError:
            pass

        # Remove superscript reference number.
        try:
            for div in soup.find_all('sup', attrs={'class': 'reference'}):
                div.extract()
        except AttributeError:
            pass

        main_section = soup.find('div', attrs={'class': 'mw-parser-output'})

        # Remove [edit] or [编辑] inside <h2> tags.
        h2s = main_section.find_all(['h2'])
        for h2 in h2s:
            h2.find('a').extract()  # Remove edit or 编辑.
            spans = h2.find_all('span',
                                attrs={'class': 'mw-editsection-bracket'})
            for span in spans:
                span.extract()  # Remove [].

        # Remove [edit] or [编辑] inside <h3> tags.
        h3s = main_section.find_all(['h3'])
        for h3 in h3s:
            h3.find('a').extract()  # Remove edit or 编辑.
            spans = h3.find_all('span',
                                attrs={'class': 'mw-editsection-bracket'})
            for span in spans:
                span.extract()  # Remove [].

        h2_h3_p_li = main_section.find_all(['h2', 'h3', 'p', 'li'])

        for tag in h2_h3_p_li:
            t = tag.get_text(strip=False)
            #TODO: remove the empty line ahead.
            t = re.sub(r'\[edit\]', '',
                       t)  #TODO: can we only check this on h2 and h3?
            yield (t)

    def save_text(self, text: 'str', title: 'str',
                  language_code: 'str') -> None:
        """Save downloaded text.
        """
        filepath = os.path.join(self.save_path, f'{title}_{language_code}.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(text)
        print(f'Text saved at {filepath}')
        return filepath

    def url_parser(self, url: 'str'):
        wiki_reg = ''
        baike_reg = ''
        if re.search(wiki_reg, url):
            self.url_parser_wiki(url)
        elif re.search(baike_reg, url):
            self.url_parser_baike(url)

    def url_parser_wiki(self, url: 'str'):
        langcode_reg = '\/\/(.*)\.wikipedia\.org'
        try:
            langcode = re.search(langcode_reg, url).group(1)
        except ValueError:
            print('Invalid Wiki URL.')

        oldid_reg = 'oldid='
        if re.search(oldid_reg, url):
            oldid = url.split(oldid_reg)[-1]
        return langcode, oldid

    def url_parser_baike(self, url: 'str'):
        pass


if __name__ == '__main__':
    # Tests
    import _global
    dm = DownloadManager(_global.CUTSPATH, debug_mode=False)

    ####################################################################
    # Test self.search_keyword()
    # q = 'steve jobs'
    # print(dm.search_keyword(q))
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

    ####################################################################
    # Test self.url_parser_wiki()
    wiki_url = 'https://en.wikipedia.org/w/index.php?title=Steve_Jobs&oldid=1095821758'
    print(dm.url_parser_wiki(wiki_url))