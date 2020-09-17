import socketserver,logging,json,subprocess
from typing import List
import requests
from .lookup_utils import wrap_word_list_into_links


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    dict_daemon=None

    def __wrap_response(self,status_code,result):
        return json.dumps({
            "status_code": status_code,
            "results":result
        },ensure_ascii=False)

    def parse_input(self,data:bytes):
        data=data.decode('utf-8')
        cmd_obj=json.loads(data)
        command=cmd_obj['command']
        kwargs=cmd_obj['kwargs']
        return command,kwargs
        #if ":" in data:
        #    command,extra=data.split(":")[:2]
        #    if extra:
        #        if ',' in extra:
        #            params=list(filter(lambda x: x != '', extra.split(',')))
        #        else:
        #            params=[extra]
        #    else:
        #        params=[]
        #    return command.strip(),list(map(lambda x: x.strip(), params))
        #else:
        #    return data.strip(),[]

    def handle(self):
        data = self.request.recv(8192).strip()
        command,kwargs=self.parse_input(data)
        print(command,kwargs)
        try:
            return_str=getattr(self,command)(**kwargs)
        except AttributeError as e:
            return_str=f'Unknown command {command}'
            logging.exception(e)
        except Exception as e:
            return_str=str(e)
            logging.exception(e)

        self.request.sendall(return_str.encode("utf-8"))

    def ListWord(self,dict_name,word):
        #dict_name=params[0]
        #word=params[1]
        logging.info(f"Search {word} in word index of {dict_name}")
        status_code=0
        _,results=self.dict_daemon.search_index(word,dict_name)
        if not results:
            status_code=1
        return self.__wrap_response(status_code,results)

    def Lookup(self,word,dicts=None):
        #word=param_list[0]
        #dicts=param_list[1:]
        logging.info(f"Lookup word {word} in {dicts if dicts else 'enabled dicts'}")
        definition_list = self.dict_daemon.lookup(word,dicts)
        status_code=0
        if not definition_list:
            status_code=2
            dict_name,words=self.dict_daemon.search_index(word)
            if not words:
                status_code=1
            else:
                definition_list={
                    dict_name:wrap_word_list_into_links(words)
                }
        #print(definition_list.get('USE THE RIGHT WORD',''))
        return self.__wrap_response(status_code,definition_list)

    def ListDicts(self,enabled=True):
        #extra=int(params[0])
        #logging.info("List dictionaries")
        #enabled=extra if extra else 1
        return self.__wrap_response(0,self.dict_daemon.list_dictionaries(enabled))

    def Test(self,params):

        headers={'Host': 'fanyi.baidu.com',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
        r=requests.get("https://fanyi.baidu.com/#en/zh/hello",headers=headers)
        return r.text


