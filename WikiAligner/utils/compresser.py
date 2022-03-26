from sentence_transformers import SentenceTransformer
import pickle


class Compresser:
    def compress_labse(self, save_path: str = './labse_model.pkl'):
        model = SentenceTransformer('sentence-transformers/LaBSE')
        with open(save_path, 'wb') as f:
            pickle.dump(model, f)
        print(f'LaBSE model have been compressed at {save_path}')