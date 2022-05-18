from typing import Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import faiss

# from utils._decorators import timer


#TODO: compare performances of each method.
#TODO: normalization
#TODO: 如果先拼合两篇文本，只加载、encode一次，再拆开，会更快吗？准确率有影响吗？
#TODO: 考虑加入perspective=0，用来放弃双向视角，取两个视角的平均最优。方法用论文中的score。双向视角可以用半个score，把2k改成k。
#TODO: 考虑perspective是否设为类的attribute？好处是不需要在每个函数内定义，代码简洁，但是可能牺牲了灵活性，每次计算都要重新实例化？
class SimCalculator:
    """Calculate similarity of each vector pair from two sentence embedding matrices. Pair the most similar vectors.

    Parameters
    ----------
    embedding1, embedding2 : 
        Matrix of float.
    """
    def __init__(self, embedding1: Union[np.ndarray, 'list[list[float]]'],
                 embedding2: Union[np.ndarray, 'list[list[float]]']) -> None:
        self.embedding1 = embedding1
        self.embedding2 = embedding2

        # faiss-specific attributes
        self.faiss_k = 4
        self.faiss_min_threshold = 1

    def sim_auto(self, method='faiss', perspective=0):
        if method == 'sklearn':
            return self.sim_with_sklearn(self.embedding1, self.embedding2,
                                         perspective)
        elif method == 'faiss':
            return self.sim_with_faiss(self.embedding1,
                                       self.embedding2,
                                       perspective=perspective)
        else:
            return 'Align method can\'t be applied. Feel free to give us suggestions via https://github.com/LukeTu/WikiAligner'

    def _margin(self, a, b):
        """According to the conclusion from Artetxe and Schwenk, 2019.
        """
        return a / b

    def _score(self, x, y, fwd_mean, bwd_mean, margin):
        return margin(x.dot(y), (fwd_mean + bwd_mean) / 2)

    def _score_candidates(self, x, y, candidate_idxs, fwd_mean, bwd_mean,
                          margin):
        scores = np.zeros(candidate_idxs.shape)
        for i in range(scores.shape[0]):
            for j in range(scores.shape[1]):
                k = candidate_idxs[i, j]
                scores[i, j] = self._score(x[i], y[k], fwd_mean[i],
                                           bwd_mean[k], margin)
        return scores

    def _faiss_prep(self, x, y, dim):
        index = faiss.IndexFlatIP(dim)  # dot product
        index.add(y)
        sim, idx = index.search(x, self.faiss_k)
        return sim, idx

    # @timer
    def sim_with_faiss(self,
                       embedding1: Union[np.ndarray, 'list[list[float]]'],
                       embedding2: Union[np.ndarray, 'list[list[float]]'],
                       dim: 'int' = 768,
                       perspective: 'int' = 0):
        """
        Parameters
        ----------
        dim : int
            Dimension of embedding vectors. Uses LaBSE's (the sentence embedding tool) default dimension (768) as default.
        
        perspective : int
            From which embedding matrix's perspective. Note that, from eb1's perspective, 
            eb1_sentence1 may be similar with eb2_sentence2 the most, 
            while from eb2's perspective, 
            eb2_sentence2 may be similar with eb1_sentence3 the most.
        """
        # index = faiss.IndexFlatL2(dim)
        # Change a shorter name. Not alias.
        x = embedding1
        y = embedding2
        #TODO: perspective=0时，两边的句子都一定有对应的吗？
        if perspective == 0:
            x_norm = x / np.linalg.norm(x, axis=1, keepdims=True)
            y_norm = y / np.linalg.norm(y, axis=1, keepdims=True)
            # axis = 1: L2-norm by row

            # Forward direction: embedding1 to embedding2
            x2y_sim, x2y_idx = self._faiss_prep(x_norm, y_norm, dim)
            x2y_sim_mean = x2y_sim.mean(axis=1)

            # Backward direction: embedding2 to embedding1
            y2x_sim, y2x_idx = self._faiss_prep(y_norm, x_norm, dim)
            y2x_sim_mean = y2x_sim.mean(axis=1)

            fwd_scores = self._score_candidates(x_norm, y_norm, x2y_idx,
                                                x2y_sim_mean, y2x_sim_mean,
                                                self._margin)
            bwd_scores = self._score_candidates(y_norm, x_norm, y2x_idx,
                                                y2x_sim_mean, x2y_sim_mean,
                                                self._margin)
            fwd_best = x2y_idx[np.arange(x.shape[0]),
                               fwd_scores.argmax(axis=1)]
            bwd_best = y2x_idx[np.arange(y.shape[0]),
                               bwd_scores.argmax(axis=1)]
            indices = np.stack([
                np.concatenate([np.arange(x.shape[0]), bwd_best]),
                np.concatenate([fwd_best, np.arange(y.shape[0])])
            ],
                               axis=1)
            scores = np.concatenate(
                [fwd_scores.max(axis=1),
                 bwd_scores.max(axis=1)])
            seen_eb1, seen_eb2 = set(), set()
            for i in np.argsort(-scores):
                eb1_idx, eb2_idx = indices[i]
                eb1_idx = int(eb1_idx)
                eb2_idx = int(eb2_idx)
                if scores[i] < self.faiss_min_threshold:
                    break
                if eb1_idx not in seen_eb1 and eb2_idx not in seen_eb2:
                    seen_eb1.add(eb1_idx)
                    seen_eb2.add(eb2_idx)
                    yield eb1_idx, eb2_idx, scores[i]

        elif perspective == 1:
            x2y_sim, x2y_idx = self._faiss_prep(x, y, dim)
            for similarity, eb2Idx, eb1Idx in zip(x2y_sim, x2y_idx,
                                                  range(len(x))):
                yield eb1Idx, eb2Idx[0], similarity[0]
        elif perspective == 2:
            y2x_sim, y2x_idx = self._faiss_prep(y, x, dim)
            for similarity, eb1Idx, eb2Idx in zip(y2x_sim, y2x_idx,
                                                  range(len(y))):
                yield eb1Idx[0], eb2Idx, similarity[0]
        else:
            raise ValueError(
                f'Invalid perspective={perspective}! Set perspective = 1 to calculate similarity from the first matrix\'s perspective, set 2 from the opposite.'
            )

    # @timer
    def sim_with_sklearn(self,
                         embedding1: Union[np.ndarray, 'list[list[float]]'],
                         embedding2: Union[np.ndarray, 'list[list[float]]'],
                         perspective: 'int' = 1):
        """Calculate a cosine similarity matrix of sentence embeddings from 2 documents with sklearn, 
        and return the largest element from every line/column of a matrx.
        
        Parameters
        ----------
        by_row : boolean
            Whether from row's perspective (i.e. from embedding1's perspective). 
            Note that, from eb1's perspective, eb1_sentence1 may be similar with eb2_sentence2 the most, 
            while from eb2's perspective, eb2_sentence2 may be similar with eb1_sentence3 the most.
        
        by_row : boolean
            Search direction. If search by row, 
            we regard sentence in language1 as the target and find the most similar one from language2. 
            This direction is to avoid a great chance to have multiple alignment pairs 
            from a column perspective rather we get max similarity by row.
        """
        #TODO: double check the meaning of <by_row>
        #TODO: 查看是否能调用所有cpu核
        matrix = np.array(cosine_similarity(embedding1, embedding2))
        if perspective == 1:
            for rowIdx in range(matrix.shape[0]):
                maxColIdx = 0
                colIdx = 0
                while colIdx < matrix.shape[1]:
                    if matrix[rowIdx][colIdx] > matrix[rowIdx][maxColIdx]:
                        maxColIdx = colIdx
                    colIdx += 1
                yield rowIdx, maxColIdx, matrix[rowIdx][maxColIdx]
        elif perspective == 2:
            for colIdx in range(matrix.shape[1]):
                maxRowIdx = 0
                rowIdx = 0
                while rowIdx < matrix.shape[0]:
                    if matrix[rowIdx][colIdx] > matrix[maxRowIdx][colIdx]:
                        maxRowIdx = rowIdx
                    rowIdx += 1
                yield maxRowIdx, colIdx, matrix[maxRowIdx][colIdx]
        else:
            ValueError(
                f'Invalid perspective={perspective}! Set perspective = 1 to calculate similarity from the first embedding matrix\'s perspective, set 2 from the opposite.'
            )


if __name__ == '__main__':
    import sys
    import os
    import json
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # BASE_DIR: WikiTrans base directory.
    sys.path.append(BASE_DIR)
    datapath = os.path.join(BASE_DIR, 'data')

    # Make a fake embedding for testing.
    d = 768  # dimension
    np.random.seed(1234)
    num_eb1 = 200  # embedding1 size
    num_eb2 = 100  # embedding2 size

    fake_eb1 = np.random.random((num_eb1, d)).astype('float32')
    # Update the first element of each array with the array's index.
    fake_eb1[:, 0] += np.arange(num_eb1) / 1000.  # 1000. = 1000.0
    fake_eb2 = np.random.random((num_eb2, d)).astype('float32')
    # Update the first element of each array with the array's index.
    fake_eb2[:, 0] += np.arange(num_eb2) / 1000.
    print('Shape:')
    print(fake_eb1.shape[0])
    print(fake_eb2.shape[0])
    print('Embedding 1: ')
    print(fake_eb1[:5])
    print('Embedding 2: ')
    print(fake_eb2[:5])
    sc = SimCalculator(fake_eb1, fake_eb2)
    json_list = []
    for eb1_idx, eb2_idx, similarity in sc.sim_auto():
        json_list.append({
            f'id_lang1': int(eb1_idx),
            f'id_lang2': int(eb2_idx),
            f'sim': float(similarity)
        })
    json_path = os.path.join(datapath, 'test_sim_calculator.json')

    with open(json_path, 'w') as jsonfile:
        json.dump(json_list, jsonfile)
