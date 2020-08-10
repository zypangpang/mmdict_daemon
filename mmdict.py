import socketserver,json,signal,sys,os
from dict_daemon.dict_daemon import DictDaemon,DictConfigs
from dict_daemon.handler import MyTCPHandler
import daemon,fire,constants
import log_config,logging,configparser
from pathlib import Path
from dict_daemon.dict_daemon import IndexBuildError

def signal_handler(sig, frame):
    global server
    try:
        server.server_close()
        os.unlink(constants.SOCKET_LOCATION)
    except Exception as e:
        logging.error(e)
    sys.exit(0)



class Main():
    """
    mmDict: A simple mdict lookup daemon
    """
    __config_file=None

    @classmethod
    def __run_server(cls):
        global server
        if constants.OS_NAME == "Linux" or constants.OS_NAME=="Darwin":
            if os.path.exists(constants.SOCKET_LOCATION):
                logging.info("mmDict already running")
                logging.info(f"If you are sure mmDict is not running, you can delete {constants.SOCKET_LOCATION} first, "
                      f"then try to run again.")
                exit(0)

            MyTCPHandler.dict_daemon=DictDaemon(cls.__config_file)

            # Register signal handler for server cleaning
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            logging.info("running with Unix socket")
            server=socketserver.UnixStreamServer(constants.SOCKET_LOCATION, MyTCPHandler)
            server.serve_forever()

        else:
            MyTCPHandler.dict_daemon=DictDaemon(cls.__config_file)
            logging.info("running with TCP socket")
            try:
                server=socketserver.TCPServer((constants.HOST,constants.PORT), MyTCPHandler)
                server.serve_forever()
            except OSError:
                logging.error(f"{constants.HOST}:{constants.PORT} is already in use.")


    @classmethod
    def run(cls,d=False,config_file=None):
        """
        run mmDict server
        :param d: run as daemon process
        :param config_file: Optional. custom config file path.
        """
        cls.__config_file=config_file
        if d:
            logging.info("Run mmDcit in background")
            with daemon.DaemonContext():
                Main.__run_server()
        else:
            Main.__run_server()

    @classmethod
    def rebuild_index(cls,dicts=None):
        '''
        Rebuild dictionary indexes
        :param dicts: Optional. dicts for rebuilding index
        '''
        dicts=dicts.split(",")
        logging.info(f"Rebuilding index for {dicts}")
        DictDaemon(load_index=False).rebuild_index(dicts)
        logging.info("Done")


    @classmethod
    def init(cls,dict_folder=None):
        '''
        Init configs. You need to run this command the first time you use mmDict.
        :param dict_folder: Optional. If given, import dictionaries in dict_folder at the same time.
        '''
        if constants.DEFAULT_CONFIG_PATH.exists():
            logging.info(f"Config file {constants.DEFAULT_CONFIG_PATH} already exists")
            logging.info("Exit.")
        else:
            os.makedirs(constants.DEFAULT_CONFIG_PATH.parent, 0o0755)
            DictConfigs.generate_init_configs()
            logging.info(f"Init config file generated as {constants.DEFAULT_CONFIG_PATH}")
            logging.info("Change 'dictionaries' and 'enabled dictionaries' field to add your dictionaries or "
                         "run 'python mmdict import <folder>' to import dictionaries")
            if dict_folder:
                cls.import_dict(dict_folder)
                logging.info("Import dictionaries success")

    @classmethod
    def __import_mdx(cls,configs,dict_folder):
        dicts = {x.stem: str(x.absolute()) for x in dict_folder.iterdir() if x.is_file() and x.suffix == '.mdx'}
        dict_daemon=DictDaemon(load_index=False)
        try:
            dict_daemon._build_indexes(dicts)
        except IndexBuildError as e:
            logging.error("Build index failed for some dictionaries")
            for x in e.error_dicts:
                dicts.pop(x)
        configs.set_dicts(dicts)
        return dicts.keys()

    @classmethod
    def __import_mdd(cls,configs,dict_folder):
        index_foler = configs.get_daemon_value("index folder")
        mdds = {x.stem: str(x.absolute()) for x in dict_folder.iterdir() if x.is_file() and x.suffix == '.mdd'}
        for dict in mdds.keys():
            Path(index_foler).joinpath(dict).mkdir(mode=0o0755, exist_ok=True)
        dict_daemon=DictDaemon(load_index=False)
        try:
            dict_daemon.extract_mdds(mdds)
        except IndexBuildError as e:
            logging.error(f"Extract some mdds failed: {e.error_dicts}")

    @classmethod
    def import_dict(cls,dict_folder,config_path=None):
        '''
        Import dictionaries from dict_folder. This will overwrite original settings in mmDict config file.
        :param config_path: Optional. update settings in custom config_path
        '''
        if not config_path:
            config_path=constants.DEFAULT_CONFIG_PATH
        configs=DictConfigs(config_path)
        dict_folder=Path(dict_folder)

        names=cls.__import_mdx(configs,dict_folder)
        cls.__import_mdd(configs,dict_folder)

        index_foler = configs.get_daemon_value("index folder")
        logging.info(f"Imported {len(names)} dictionaries: {names}")
        logging.info(f"If the dictionary has css or js related, you need to copy them into {index_foler}/<dict_name> manually")

    #@classmethod
    #def add_dict(cls,mdx_path,config_path=None):
    #    '''
    #    Add dict to config file
    #    :param mdx_path: dictionary mdx file path
    #    :param config_path: Optional. update settings in custom config_path
    #    '''
    #    if not config_path:
    #        config_path=constants.DEFAULT_CONFIG_PATH
    #    configs=DictConfigs(config_path)
    #    name=configs.add_dict(mdx_path)
    #    logging.info(f"Added dictionary {name}")

    @classmethod
    def list_dicts(cls,enabled=True):
        """
        List dictionaries
        :param enabled: Only list enabled dicts or all dicts. Default True
        """
        print('\n'.join(DictDaemon(constants.DEFAULT_CONFIG_PATH,False).list_dictionaries(enabled)))


if __name__ == "__main__":
    fire.Fire(Main)

