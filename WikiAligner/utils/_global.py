"""Global variables"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # BASE_DIR: WikiTrans base directory.
MODEL_PATH = os.path.join(BASE_DIR, 'models')
DATAPATH = os.path.join(BASE_DIR, 'data')
CUTSPATH = os.path.join(DATAPATH, 'cuts')  # Saves original TXT and cutted TXT.
EMBEDPATH = os.path.join(DATAPATH, 'embeds')  # Saves embedding vectors.
SIMPATH = os.path.join(DATAPATH,
                       'sim_json')  # Saves similarity results in JSON.

sys.path.append(BASE_DIR)
global_paths = [DATAPATH, CUTSPATH, EMBEDPATH, SIMPATH]

for path in global_paths:
    if not os.path.exists(path): os.makedirs(path)

# Not only make the path, but also compress the models if the path doesn't exist or it's empty.
if not os.path.exists(MODEL_PATH) or os.listdir(MODEL_PATH) == []:
    os.makedirs(MODEL_PATH)
    import compresser
    compresser.main()

if __name__ == '__main__':
    with open(os.path.join(BASE_DIR, 'utils', 'labse_languages.txt')) as f:
        languages = f.readlines()
