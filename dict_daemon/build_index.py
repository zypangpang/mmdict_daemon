from collections import defaultdict

from dict_parse.mymdict import MDX,MDD
import json,zlib,os,logging,constants
from sys import getsizeof

class IndexManipulator():

    index_path_prefix=None
    mem_opt=False

    '''
    @classmethod
    def build_indexes(cls,dict_paths,rebuild=False):
        error_dict=[]
        for name,path in dict_paths.items():
            try:
                cls._build_index(name,path,rebuild)
            except Exception as e:
                logging.error(f"Cannot build index for {name}, error = {e}")
                error_dict.append(name)
    '''


    @classmethod
    def extract_mdd(cls,dict_name, mdd_path):
        mdd=MDD(mdd_path)
        folder=os.path.join(cls.index_path_prefix,dict_name)
        mdd.write_to_folder(folder)


    @classmethod
    def get_index_file_name(cls,dict_name):
        if not cls.index_path_prefix:
            raise Exception("Internal error: index_path_prefix is not set")
        return os.path.join(cls.index_path_prefix,dict_name+".index")

    @classmethod
    def build_index(cls,dict_name,dict_path,rebuild):
        '''

        :param dict_name:
        :param dict_path:
        :param rebuild:
             :return:

        Index format:
        {
            'b':[
                (record_block_begin_offset, compressed_size, decompressed_size),...
            ],
            'k':{
                'word': [
                            (record_block_index, key_begin_offset,key_end_offset),
                            (),
                            ()
                        ],...
            }
        }
        '''
        path=cls.get_index_file_name(dict_name)
        if not rebuild and os.path.exists(path):
            return
        if not os.path.exists(dict_path):
            logging.error(f"{dict_path} not exist")
            return

        logging.info(f"building index for new dictionary {dict_name} ...")

        mdx = MDX(dict_path)
        block_info=mdx.get_block_info()
        key_offsets=defaultdict(list)
        for key,index in mdx.items():
            key_offsets[key].append(index)

        #key_offsets = {key: index for key, index in mdx.items()}
        index_obj={
            'b':block_info,
            'k':key_offsets
        }
        jsonbytes = json.dumps(index_obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        compressed_bytes = zlib.compress(jsonbytes)
        with open(path, "wb") as f:
            f.write(compressed_bytes)


    @classmethod
    def load_index(cls,dict_name):
        path=cls.get_index_file_name(dict_name)
        if not os.path.exists(path):
            raise Exception(f"No index file for {dict_name}")
        with open(path, "rb") as f:
            compressed_bytes = f.read()
        if not cls.mem_opt:
            #print(getsizeof(compressed_bytes))
            decompressed = zlib.decompress(compressed_bytes)
            #print(getsizeof(decompressed))
            return json.loads(decompressed.decode("utf-8"))
        else:
            return compressed_bytes

    @classmethod
    def get_index_obj(cls, index_bytes):
        if cls.mem_opt:
            decompressed = zlib.decompress(index_bytes)
            return json.loads(decompressed.decode("utf-8"))
        else:
            return index_bytes


    '''
    @classmethod
    def load_indexes(cls,dict_names):
        cls.index_obj={}
        for name in dict_names:
            try:
                cls._load_index(name)
            except Exception as e:
                print(e)

        return cls.index_obj


    @classmethod
    def get_index(cls,dict_name):
        if cls.index_obj is None:
            raise Exception("Please load index first")
        return cls.index_obj[dict_name]
    '''

if __name__ == '__main__':
    IndexManipulator.index_path_prefix="./"
    IndexManipulator.build_index("test", "/mnt/document/Dictionary/USE THE RIGHT WORD.mdx",False)

