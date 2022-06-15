# WikiAligner

## Instruction for deploying front-end(temporary deprecation)

~~The running of front-end requires a Apache environment, which has been included in the [XMAPP](https://www.apachefriends.org/index.html), a cross-platform web server solution stack package.~~

~~After the installation of xmapp, go to the Control Panel and config the `Apache(httpd.conf)` under the Apache Module:~~

1. ~~Locate the below string:~~ 

```bash
DocumentRoot "X:/xampp/htdocs"

<Directory "X:/xampp/htdocs">
```

2. ~~Modify **both** of the path to a same new route, say:~~

```bash
DocumentRoot "C:\Web"

<Directory "C:\Web">
```

3. ~~Copy the files from the frontend folder to the designated new route.~~
4. ~~Start the Apache Module from the XAMPP Control Panel.~~
5. ~~Go to the link `127.0.0.1` via your browser, the service should be functional now.~~

## Instruction for deploying back-end

We recommend a (mini)conda environment to run the back-end codes.

Try [this file](https://github.com/LukeTu/WikiAligner/blob/main/WikiAligner/requirements2.txt) if requirements installation failed. For installing faiss, please refer to [its document](https://github.com/facebookresearch/faiss/blob/main/INSTALL.md).

```shell
# Install faiss CPU version
$ conda install -c pytorch faiss-cpu
# Install faiss GPU+CPU version
$ conda install -c conda-forge faiss-gpu
```

While according to faiss document, the GPU version is not available other than Linux, so that here we tested with the CPU version.

To run the back-end, the LABSE model has to be downloaded and compressed first:

```shell
$ python WikiAligner/WikiAligner/utils/comresser.py
```

Then, the back-end can be initialized at:

```shell
$ python WikiAligner/WikiAligner/bin/wikitrans.py
```



## Updates

- 2022-05-26

  #### Milestone

  1. Back-end has been fully connected to the front-end.

  2. Capable to find alignments on the latest Wikipedia Articles 

  3. Running on port-forwarding.

  4. Demo has passed

     

- 2022-04-06

  #### Milestone

  1. Finished CLI after refactoring code.

  2. Successfully passed back-front connection demo locally.

  3. Applied generator to save memory.

     

- 2022-03-26

  1. Code refactorization is in progress...
  2. Working on flask for back-front connection...
  3. Debugging Wiki parse API... (might get the plain text from HTML with beautifulsoup)



## Tasks

- [ ] Front-end interface optimization [*]
- [ ] Find alignment from revisions [*]
- [x] Downloading files (Spreadsheet) [***]
- [ ] Analysis and filtering of identical requests [*]
- [ ] Process optimization, queuing requests [******]
- [ ] Split language model parsing, caching judgement on steps [***]
- [ ] Add switch to double URL retrieval (Wikipedia/Custom) [*]
- [ ] Download and parsing to URL search [***]
- [ ] File upload [**]

[*] stands for difficulties

## TODO

- [ ] Write API document for back-front connection... 
- [x] Build a function that export <sentence> + <similarity score> in a single .xlsx file; user can download it...
- [x] Check out similarity result (United Nations document may as an option of standard example)...
- [ ] Try docker or other methods for environment migration...
- [x] Find available host and deploy demo..
- [x] Continue to refactor code further for CLI -> flask...
- [ ] Continue to optimize generator and internal API to save memory and time...
- [ ] Debugging Wiki parse API... (might get the plain text from HTML with beautifulsoup)

