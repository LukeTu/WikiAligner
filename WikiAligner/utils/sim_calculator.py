from typing import Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from utils._decorators import timer

#TODO: What about replace the term "align" with "calculate similarity" in this module?
# Align is abstract, while similarity is concrete.


#TODO: compare performances of each method.
#TODO: normalization
#TODO: 如果先拼合两篇文本，只加载、encode一次，再拆开，会更快吗？准确率有影响吗？
#TODO: Unite by_row and from_eb1 to self.perspective
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

    def sim_auto(self, method='sklearn'):
        if method == 'sklearn':
            by_row = True if input(
                'Align by row? T/F').upper() == 'T' else False
            return self.sim_with_sklearn(self.embedding1, self.embedding2,
                                         by_row)
        elif method == 'faiss':
            from_eb1 = True if input(
                'Align from embedding1\'s perspective? T/F').upper(
                ) == 'T' else False
            return self.sim_with_faiss(self.embedding1,
                                       self.embedding2,
                                       from_eb1=from_eb1)
        else:
            return 'Align method can\'t be applied. Feel free to give us suggestions via https://github.com/LukeTu/WikiAligner'

    # @timer
    def sim_with_sklearn(self,
                         embedding1: Union[np.ndarray, 'list[list[float]]'],
                         embedding2: Union[np.ndarray, 'list[list[float]]'],
                         by_row=True):
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
        if by_row:
            for rowIdx in range(matrix.shape[0]):
                maxColIdx = 0
                colIdx = 0
                while colIdx < matrix.shape[1]:
                    if matrix[rowIdx][colIdx] > matrix[rowIdx][maxColIdx]:
                        maxColIdx = colIdx
                    colIdx += 1
                yield rowIdx, maxColIdx, matrix[rowIdx][maxColIdx]
        else:
            for colIdx in range(matrix.shape[1]):
                maxRowIdx = 0
                rowIdx = 0
                while rowIdx < matrix.shape[0]:
                    if matrix[rowIdx][colIdx] > matrix[maxRowIdx][colIdx]:
                        maxRowIdx = rowIdx
                    rowIdx += 1
                yield maxRowIdx, colIdx, matrix[maxRowIdx][colIdx]

    # @timer
    def sim_with_faiss(self,
                       embedding1: Union[np.ndarray, 'list[list[float]]'],
                       embedding2: Union[np.ndarray, 'list[list[float]]'],
                       dim=768,
                       from_eb1=True):
        """
        Parameters
        ----------
        dim : int
            Dimension of embedding vectors. Uses LaBSE's (the sentence embedding tool) default dimension (768) as default.
        
        from_eb1 : boolean
            Whether from embedding1's perspective. Note that, from eb1's perspective, 
            eb1_sentence1 may be similar with eb2_sentence2 the most, 
            while from eb2's perspective, 
            eb2_sentence2 may be similar with eb1_sentence3 the most.
        """
        index = faiss.IndexFlatL2(dim)
        if from_eb1:
            index.add(embedding2)
            D, I = index.search(embedding1, 1)
            for similarity, eb2Idx, eb1Idx in zip(D, I,
                                                  range(len(embedding1))):
                yield eb1Idx, eb2Idx[0], similarity[0]
        else:
            index.add(embedding1)
            D, I = index.search(embedding2, 1)
            for similarity, eb1Idx, eb2Idx in zip(D, I,
                                                  range(len(embedding2))):
                yield eb1Idx[0], eb2Idx, similarity[0]