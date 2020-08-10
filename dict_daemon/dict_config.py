import configparser
from pathlib import Path
from constants import CONFIG_DAEMON_SECTION,CONFIG_FRONTEND_SECTION,DEFAULT_CONFIG_PATH

class DictConfigs():
    DICT_FILED="dictionaries"
    ENABLED_FILED="enabled dictionaries"

    @classmethod
    def generate_init_configs(cls):
        index_folder = DEFAULT_CONFIG_PATH.parent.joinpath("index")
        configs = configparser.ConfigParser()
        configs[CONFIG_DAEMON_SECTION] = {
            "index folder": str(index_folder),
            cls.DICT_FILED: "/home/user/example.mdx",
            cls.ENABLED_FILED: "example.mdx"
        }
        configs[CONFIG_FRONTEND_SECTION] = {}
        with open(DEFAULT_CONFIG_PATH, "w") as f:
            configs.write(f)

    def __init__(self,file_path):
        self.config_path=file_path
        self.config=configparser.ConfigParser()
        self.config.read(file_path)

    def set_dicts(self,dicts:dict):
        #dict_names=[Path(x).stem for x in dict_paths]
        self.config[CONFIG_DAEMON_SECTION][self.DICT_FILED]=','.join(dicts.values())
        self.config[CONFIG_DAEMON_SECTION][self.ENABLED_FILED]=','.join(dicts.keys())
        with open(self.config_path,"w") as f:
            self.config.write(f)
        return dicts.keys()

    def add_dict(self,dict_path):
        dict_name=Path(dict_path).stem
        self.config[CONFIG_DAEMON_SECTION][self.DICT_FILED]+=f",{dict_path}"
        self.config[CONFIG_DAEMON_SECTION][self.ENABLED_FILED]+=f",{dict_name}"
        with open(self.config_path,"w") as f:
            self.config.write(f)
        return dict_name


    def get_config(self,section_name):
        if section_name in self.config.sections():
            return self.config[section_name]
        raise Exception(f"No config section {section_name}")

    def get_value(self, section, key):
        return self.config[section][key]

    def get_daemon_value(self, key):
        return self.config[CONFIG_DAEMON_SECTION][key]

    def get_frontend_value(self, key):
        return self.config[CONFIG_FRONTEND_SECTION][key]

    def get_dictionary_paths(self):
        dicts = self.get_value("dictionary daemon", "dictionaries").split(",")
        dicts=[x.strip() for x in dicts]
        index_folder=Path(self.get_daemon_value("index folder"))
        ans={}
        for path in dicts:
            path=Path(path)
            name=path.stem
            data_folder=str(index_folder.joinpath(name))
            ans[name]=[str(path),data_folder]
        return ans


    def get_enabled_dicts(self):
        try:
            dicts=self.get_daemon_value("enabled dictionaries")
        except Exception as e:
            return []
        return [x.strip() for x in dicts.split(',')] if dicts else []



if __name__ == '__main__':
    pass
