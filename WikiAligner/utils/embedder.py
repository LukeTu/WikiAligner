import pickle


class Embedder:
    def embed_with_labse(self, model_path, text):
        with open(model_path, 'rb') as f:
            labse_model = pickle.load(f)
        return labse_model.encode(text)
