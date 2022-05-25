import pandas as pd
import numpy as np
import codecs
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Res:
    def __init__(self) -> None:
        self.data_path = os.path.join(BASE_DIR, 'data')
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        pass

    def res_info(self, keyword='', language_code1='', wiki_title1='', language_code2='', wiki_title2=''):
        self.file_exits(keyword, language_code1, wiki_title1, language_code2, wiki_title2)
        return {'keyword': keyword, 'wiki_title1': wiki_title1, 'language_code1': language_code1,
                'path': self.data_path}

    def file_exits(self, keyword, language_code1, wiki_title1, language_code2, wiki_title2):
        if True:
            lTable = self.get_file_table(keyword, language_code1)
            rTable = self.get_file_table(keyword, language_code2)
            simTable = self.get_json_file(keyword, language_code1, language_code2)
            # max_sim=simTable.max()['sim']
            # min_sim=simTable.min()['sim']
            max_sim = 0
            min_sim = 0
            list_left = self.compute_left(lTable, simTable, language_code1, language_code2)
            list_right = self.compute_right(rTable, simTable, language_code1, language_code2)
            self.save_json(keyword, language_code1, language_code2, list_left, list_right,max_sim,min_sim)
        return True

    def get_file_table(self, keyword: str, language_code: str):
        sTable = pd.read_table('''%s\\%s_%s_seg.txt''' % (self.data_path, keyword, language_code), header=None,
                               skip_blank_lines=False)
        sTable.columns = ['text']
        sTable['id'] = sTable.index
        return sTable

    def get_json_file(self, keyword, language_code1, language_code2):
        with open('''%s\\%s_%s_%s.json''' % (self.data_path, keyword, language_code1, language_code2), 'r') as rf:
            data = json.load(rf)
            data_str = open('''%s\\%s_%s_%s.json''' % (self.data_path, keyword, language_code1, language_code2)).read()
            df = pd.read_json(data_str, orient='records')
            return df if df.size==0 else []


    def compute_left(self, l_table, sim_table, language_code1, language_code2):
        list_left = []
        for index, row in l_table.iterrows():
            sTemp = sim_table[sim_table['id_' + language_code1] == index]
            recent_date = sTemp['sim'].max()
            sim_row = sTemp[sTemp['sim'] == recent_date].reset_index(drop=True)
            if len(sim_row) > 0:
                list_left.append(
                    {"content": row['text'], 'id_L': index, 'id_R': sim_row.at[0, 'id_' + language_code2],
                     'pair_id': index, 'sim': sim_row.at[0, 'sim']})
            else:
                list_left.append({"content": row['text'], 'id_L': index, 'id_R': index, 'pair_id': -1, 'sim': -1})
        return list_left

    def compute_right(self, rTable, simTable, language_code1, language_code2):
        list_right = []
        for index, row in rTable.iterrows():
            s_temp = simTable[simTable['id_' + language_code2] == index]
            recent_date = s_temp['sim'].max()
            sim_row = s_temp[s_temp['sim'] == recent_date].reset_index(drop=True)
            if len(sim_row) > 0:
                list_right.append(
                    {"content": row['text'], 'id_L': sim_row.at[0, 'id_' + language_code1], 'id_R': index,
                     'pair_id': sim_row.at[0, 'id_' + language_code1], 'sim': sim_row.at[0, 'sim']})
            else:
                list_right.append({"content": row['text'], 'id_L': index, 'id_R': index, 'pair_id': -1, 'sim': -1})
        return list_right

    def save_json(self, keyword, language_code1, language_code2, list_left, list_right,max_sim,min_sim):
        res = {'maxSim':max_sim,'minSim':min_sim,'left': list_left, 'right': list_right}
        res2 = json.dumps(res, cls=NpEncoder)
        f = codecs.open('''%s\\%s_%s_%s_res.json''' % (self.data_path, keyword, language_code1, language_code2), 'w',
                        'utf-8')
        f.write(res2)
        f.close()


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
