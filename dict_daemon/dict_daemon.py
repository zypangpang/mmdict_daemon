import logging,os,subprocess
from dict_daemon.dict_config import DictConfigs
from dict_daemon.build_index import IndexManipulator
from dict_daemon import lookup_utils
from pathlib import Path
from inet_dicts.BaiduFanyi import BaiduFanyi
from inet_dicts import inet_dict_map

class IndexBuildError(Exception):
    def __init__(self,error_dicts):
        self.error_dicts=error_dicts

class DictDaemon():
    def __init__(self,configs,load_index=True):
        logging.info("Loading configs... ")
        self.dictionaries=configs.get_dictionary_paths()
        self.index_prefix=configs.get_daemon_value("index folder")
        self.enabled_dicts=configs.get_enabled_dicts()

        IndexManipulator.index_path_prefix = self.index_prefix
        IndexManipulator.mem_opt = int(configs.get_daemon_value("mem opt"))

        if load_index:
            logging.info("Building indexes... ")
            self._build_indexes()

            logging.info("Loading indexes... ")
            self._load_indexes()


    def _load_indexes(self):
        self.index_bytes={}
        for name in self.enabled_dicts:
            if name in inet_dict_map:
                continue
            self.index_bytes[name] = IndexManipulator.load_index(name)

    def _build_indexes(self,dicts=None,rebuild=False,):
        if not os.path.exists(self.index_prefix):
            logging.info("Index folder not exists. Creating...")
            os.makedirs(self.index_prefix)

        if not dicts:
            dicts={key: self.dictionaries[key][0] for key in self.dictionaries}

        error_dicts=[]
        for name,path in dicts.items():
            try:
                IndexManipulator.build_index(name,path,rebuild)
            except Exception as e:
                logging.error(f"Build index for {name} failed, error = {e}")
                error_dicts.append(name)
        if error_dicts:
            raise IndexBuildError(error_dicts)


    def rebuild_index(self,dict_names=None):
        if dict_names:
            dicts = {key: self.dictionaries[key][0] for key in dict_names}
        else:
            dicts=None
        self._build_indexes(rebuild=True,dicts=dicts)
        #self._load_indexes()

    def _lookup_mdx(self,word,dict_name):
        dict_index = IndexManipulator.get_index_obj(self.index_bytes[dict_name])
        if word not in dict_index['k']:
            raise Exception(f"No '{word}' entry in {dict_name}")
        key_offset_list = dict_index['k'][word]
        result_list = []
        for key_offset in key_offset_list:
            index_tuple = dict_index['b'][key_offset[0]] + key_offset[1:]
            result_list.append(lookup_utils.decode_record_by_index(self.dictionaries[dict_name][0], index_tuple))
        return '<br/><br/>'.join(result_list)

    def _lookup(self,word,dict_name):
        if dict_name in inet_dict_map:
            res=inet_dict_map[dict_name].lookup(word)
            return res
        return self._lookup_mdx(word,dict_name)


    def lookup(self,word,dicts=None):
        ans={}
        if not dicts:
            dicts=self.enabled_dicts
        for d in dicts:
            try:
                ans[d]=self._lookup(word,d)
            except Exception as e:
                logging.error(f"Lookup '{word}' in '{d}' failed, error = {e}")
        return ans

    def list_all_words(self,dict_name):
        if dict_name not in self.index_bytes:
            raise Exception(f"Unknown dict: {dict_name}")
        return filter(lambda word: word[0]!='@', self.index_bytes[dict_name]['k'].keys())

    def search_index(self,word,dict_name=None):
        if not dict_name:
            dict_name=self.enabled_dicts[0]
        all_words = self.list_all_words(dict_name)
        results = subprocess.run(['fzy', '-e', word], input='\n'.join(all_words),
                                 check=True, text=True, capture_output=True).stdout.split('\n')
        results = results[:20]
        return dict_name,results

    def list_dictionaries(self,enabled=True):
        #if enabled:
            #return [[name]+self.dictionaries[name] for name in self.enabled_dicts]
        return self.enabled_dicts
        #else:
        #    return [[name]+self.dictionaries[name] for name in self.dictionaries.keys()]

    def extract_mdds(self,mdds:dict):
        error_dicts=[]
        for name,path in mdds.items():
            logging.info(f"Extract mdd {name}...")
            try:
                IndexManipulator.extract_mdd(name,path)
            except Exception as e:
                logging.error(f"Extract {name}.mdd failed, error = {e}")
                error_dicts.append(name)

        if error_dicts:
            raise IndexBuildError(error_dicts)





if __name__ == '__main__':
    daemon=DictDaemon()
    ans=daemon.lookup("write")
    print(ans)

