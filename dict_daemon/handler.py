import socketserver,logging,json,subprocess
from typing import List
import requests


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    dict_daemon=None

    def parse_input(self,data:bytes):
        data=data.decode('utf-8')
        if ":" in data:
            command,extra=data.split(":")[:2]
            if extra:
                if ',' in extra:
                    params=list(filter(lambda x: x != '', extra.split(',')))
                else:
                    params=[extra]
            else:
                params=[]
            return command.strip(),list(map(lambda x: x.strip(), params))
        else:
            return data.strip(),[]

    def handle(self):
        data = self.request.recv(8192).strip()
        command,params=self.parse_input(data)
        print(command,params)
        try:
            return_str=getattr(self,command)(params)
        except AttributeError as e:
            return_str=f'Unknown command {command}'
            logging.exception(e)
        except Exception as e:
            return_str=str(e)
            logging.exception(e)

        self.request.sendall(return_str.encode("utf-8"))

    def ListWord(self,params:List[str]):
        dict_name=params[0]
        word=params[1]
        logging.info(f"Search {word} in word index of {dict_name}")
        all_words=self.dict_daemon.list_all_words(dict_name)
        results = subprocess.run(['fzy', '-e', word], input='\n'.join(all_words),
                                 check=True, text=True, capture_output=True).stdout.split('\n')
        results = results[:20]
        return ','.join(results)

    def Lookup(self,param_list:List[str]):
        word=param_list[0]
        dicts=param_list[1:]
        logging.info(f"Lookup word {word} in {dicts if dicts else 'enabled dicts'}")
        definition_list:dict = self.dict_daemon.lookup(word,dicts)
        #print(definition_list.get('USE THE RIGHT WORD',''))
        return json.dumps(definition_list,ensure_ascii=False)

    def ListDicts(self,params):
        extra=int(params[0])
        logging.info("List dictionaries")
        enabled=extra if extra else 1
        return json.dumps(self.dict_daemon.list_dictionaries(enabled),ensure_ascii=False)

    def Test(self,params):

        headers={'Host': 'fanyi.baidu.com',
                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}
        r=requests.get("https://fanyi.baidu.com/#en/zh/hello",headers=headers)
        return r.text


