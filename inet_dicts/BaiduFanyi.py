import http.client
import hashlib
import urllib
import random
import json
import configs
import logging

class BaiduFanyi:

    # 百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
    # coding=utf-8

    appid = configs.BAIDU_APPID  # 填写你的appid
    secretKey = configs.BAIDU_SECRETKEY  # 填写你的密钥
    myurl = '/api/trans/vip/translate'

    @classmethod
    def toHtml(cls,result):
        res=result['trans_result']
        return '<br>'.join([r['dst'] for r in res])

    @classmethod
    def lookup(cls,q:str):
        q=q.strip()

        fromLang = 'auto'  # 原文语种
        toLang = 'en'  # 译文语种
        if q.encode('utf-8').isalpha():
            toLang='zh'

        httpClient = None

        salt = random.randint(32768, 65536)
        sign = cls.appid + q + str(salt) + cls.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = cls.myurl + '?appid=' + cls.appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
            salt) + '&sign=' + sign + '&dict=0'

        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com',timeout=5)
            httpClient.request('GET', myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)

            return cls.toHtml(result)

        except Exception as e:
            logging.error(e)
            return "Error"

        finally:
            if httpClient:
                httpClient.close()
