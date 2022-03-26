import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import faiss

from _decorators import timer


class Aligners:
    # @timer
    def align_with_sklearn(embedding1: np.ndarray,
                           embedding2: np.ndarray,
                           by_row=True):
        """Calculate a cosine similarity matrix of sentence embeddings from 2 documents with sklearn, and return the largest element from every line/column of a matrx.
        
        : by_row : boolean, whether from row's perspective (i.e. from embedding1's perspective). Note that, from eb1's perspective, eb1_sentence1 may be similar with eb2_sentence2 the most, while from eb2's perspective, eb2_sentence2 may be similar with eb1_sentence3 the most.
        
        : by_row : boolean, search direction. If search by row, we regard sentence in language1 as the target and find the most similar one from language2. This direction is to avoid a great chance to have multiple alignment pairs from a column perspective rather we get max similarity by row.
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
    def align_with_faiss(embedding1, embedding2, dim=768, from_eb1=True):
        """
        : dim : int, dimension of embedding vectors. Uses LaBSE's default dimension (768) as default.
        
        : from_eb1 : boolean, whether from embedding1's perspective. Note that, from eb1's perspective, eb1_sentence1 may be similar with eb2_sentence2 the most, while from eb2's perspective, eb2_sentence2 may be similar with eb1_sentence3 the most.
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