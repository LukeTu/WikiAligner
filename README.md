# WikiAligner
Try [this file](https://github.com/LukeTu/WikiAligner/blob/main/WikiAligner/requirements2.txt) if requirements installation failed. For installing faiss, please refer to [its document](https://github.com/facebookresearch/faiss/blob/main/INSTALL.md).
```
# Install faiss CPU version
conda install -c pytorch faiss-cpu
# Install faiss GPU+CPU version
conda install -c conda-forge faiss-gpu
```
While according to faiss document, the GPU version is not available other than Linux, so that here we tested with the CPU version.

- 2022-04-06
  #### Milestone
  1. Finished CLI after refactoring code.
  2. Successfully passed back-front connection demo locally.
  3. Applied generator to save memory.
  #### TODO
  1. Find available host and deploy demo...
  2. Continue to refactor code further for CLI -> flask...
  3. Continue to optimize generator and internal API to save memory and time...
  4. Debugging Wiki parse API... (might get the plain text from HTML with beautifulsoup)

- 2022-03-26
  1. Code refactorization is in progress...
  2. Working on flask for back-front connection...
  2. Debugging Wiki parse API... (might get the plain text from HTML with beautifulsoup)
