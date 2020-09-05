## mmDict
**mmDict** is another mdict dictionary which parses mdx/mdd file and serve word definitions. 
What makes mmDict distinct is the use of Server/Client model. 

It is only tested on Linux yet, but it should work both on macOS and windows with little tweak. <br>
**It is recommended to deploy on Linux.** You can then use mmDict client on whichever OS you like.

This repo is the server daemon. Various clients can be developed using the same interface. 
Two simple clients can be found [here](https://github.com/zypangpang/mmdict_client).

### Features
* Build index once and quick search after.
* Compressed index file and remove redundancy to optimize mem usage
* Easily configure with ini config format
* Easily import mdx dictionaries and mdd data files.
* Support both unix socket and TCP socket
* Pure python implementation with as few dependencies as possible

## Dependencies
* System dependencies: 
    * Python3.6+ 
    * fzy (for quick fuzzy search)
* Python dependencies: 
    * python-lzo
    * fire
    * python-daemon (for convenient daemonization. You can omit it if you just use nohup.)
## Install
Since it is constructed by pure Python, after installing above dependencies, cloning this repo should be enough.

## Usage
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

