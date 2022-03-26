import wikipedia

from download_manager import DownloadManager

_prompt_query = '=' * 5 + 'The keyword you\'d like to search:' + '=' * 5
_prompt_wiki_title_options = '=' * 5 + 'Available language codes and their Wiki titles' + '=' * 5
_prompt_choose_keyword = 'Choose the index of your Wiki keyword from those related ones:'


class DownloadCommand:
    def _get_query(self, prompt):
        if prompt:
            print(prompt)
        query = input() or None
        return query

    keyword_options = wikipedia.search(query=_get_query(_prompt_query),
                                       results=20)
