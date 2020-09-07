## mmDict
**mmDict** is another mdict dictionary which parses mdx/mdd file and serve word definitions. 
What makes mmDict distinct is the use of Server/Client model. 

It is only tested on Linux yet, but it should work both on macOS and windows with little tweak. <br>
**It is recommended to deploy on Linux.** You can then use mmDict client on whichever OS you like.

This repo is the server daemon. Various clients can be developed using the same interface. 
Two simple clients can be found [here](https://github.com/zypangpang/mmdict_client).

**Note: Both the server and clients are on an early stage. It might be unstable with bugs. Looking forward to any 
feedback. Feel free to create issues.**

### Comparison with [GoldenDict](https://github.com/goldendict/goldendict)
GoldenDict is a fantastic mdict client I have used for a long time. But it has several 
main drawbacks, which makes me decide to create the new mmDict.
* The main design objective of mmDict is keeping as simple as possible. It only focuses on the core task, i.e. word lookup.
  GoldenDict is mature and feature-rich, which also means bloat.
* mmDict is written in pure Python and keeps as few dependencies as possible.
* mmDict crosses platforms more easily.
* The Server/Client model makes it possible to deploy once, run everywhere. You don't need to copy your dictionary 
  files and install goldendict on each device.
* The Server/Client model makes it easy to develop different clients. 

### Features
* Build index once and quick search after.
* Compressed index file and remove redundancy to optimize mem usage
* Easily configure with ini config format
* Easily import mdx dictionaries and mdd data files.
* Support both unix socket and TCP socket
* Pure python implementation with as few dependencies as possible

### Dependencies
* System dependencies: 
    * Python3.6+ 
    * fzy (for quick fuzzy search)
* Python dependencies: 
    * python-lzo
    * fire
    
### Install
Since it is constructed by pure Python, after installing above dependencies, cloning this repo should be enough.

### Usage
First run `python mmdict.py init` to init config file. Default file path is `$HOME/.mmdict/configs.ini`.
Then run `python mmdict.py import_dict <dict_dir>` to import dictionary files automatically. After doing these, 
run `python mmdict.py run` to test the program. Note that the first time you `run`, it will build indexes for all 
dictionaries which may cost seconds to minutes depending on your dictionary file.

Run `python mmdict.py -h` for help. Run `python mmdict.py <command> -h` for specific command help.
```
NAME
    mmdict.py - mmDict: A simple mdict lookup daemon

SYNOPSIS
    mmdict.py COMMAND | -

DESCRIPTION
    mmDict: A simple mdict lookup daemon

COMMANDS
    COMMAND is one of the following:

     import_dict
       Import dictionaries from dict_folder. This will overwrite original settings in mmDict config file.

     init
       Init configs. You need to run this command the first time you use mmDict.

     list_dicts
       List dictionaries

     rebuild_index
       Rebuild dictionary indexes

     run
       run mmDict server
```

### Acknowledgement
The mdict parse codes are from:
* [mdict-analysis](https://bitbucket.org/xwang/mdict-analysis)
* [writemdict](https://github.com/zhansliu/writemdict)

Great thanks to their work. All rights of related codes belong to the authors.

