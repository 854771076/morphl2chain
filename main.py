from web3 import Web3
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from  fake_useragent import UserAgent
from eth_account.messages import encode_defunct
import requests
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import threading
from functools import *
logger.add(
    "Morphl2_Bot.log",
    rotation="1 week",
    retention="1 month",
    level="INFO",
    format="{time} {level} {message}",
    compression="zip"  # 轮换日志文件时进行压缩
)

def log(msg):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wallet = kwargs.get('wallet')  # 使用默认值处理没有 wallet 的情况
            if wallet:
                name = wallet.get('name')  # 从 wallet 中获取 name
                try:
                    data=func(*args, **kwargs)
                    logger.success(f'{name}-{msg}成功')
                    return data
                except Exception as e:
                    logger.error(f'{name}-{msg}失败: {e}')
            else:
                try:
                    data=func(*args, **kwargs)
                    logger.success(f'{msg}成功')
                    return data
                except Exception as e:
                    logger.error(f'{msg}失败: {e}')
            
        return wrapper
    return decorator

ua=UserAgent()
class Morphl2_Bot:
    headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # Already added when you pass json=
            # 'Content-Type': 'application/json',
            # Requests sorts cookies= alphabetically
            'Origin': 'https://www.morphl2.io',
            'Pragma': 'no-cache',
            'Referer': 'https://www.morphl2.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': ua.chrome,
            'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    _lock=threading.Lock()
    def __init__(self,rpc_url = 'https://rpc-holesky.morphl2.io',private_key=''):
        '''
        rpc_url RPC接口
        '''
        self.rpc_url=rpc_url
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # 检查连接是否成功
        if not self.web3.is_connected():
            raise Exception("无法连接到 Morphl2 节点")
        self.private_key = private_key
        if private_key:
            self.account = self.web3.eth.account.from_key(private_key)        
        self.chain_id=2810
    def get_key(self,projectId=None,votingPower=None):
        address=self.account.address
        with open('encrypt.js','r',encoding='utf8') as f:
            if not projectId and not votingPower:
                js_str=f.read()
                js=execjs.compile(js_str)
                return js.call('get_data',address)
            else:
                js_str=f.read()
                js=execjs.compile(js_str)
                return js.call('get_data',address,projectId,votingPower)
    @log('获取未使用的投票')  
    def unused_voting_power(self):
        params = {
            'address': self.account.address,
        }
        response = requests.get('https://events-api-holesky.morphl2.io/activities/personal_stats', params=params, headers=self.headers)
        total=int(response.json()['data']['total_voting_power'])
        used=int(response.json()['data']['total_voted'])
        return total-used
    def sign_msg(self):
        msg='Welcome to Morph!\n\nThis is only for address check purposes, it will not trigger a blockchain transaction or cost any gas fees.\n'
        # 使用web3.py编码消息
        message_encoded = encode_defunct(text=msg)
        # 签名消息
        signed_message = self.web3.eth.account.sign_message(message_encoded,self.private_key)
        # 打印签名的消息
        return signed_message.signature.hex()
    @log('开盲盒')  
    def open_blind_box(self):
        key=self.get_key()
        json_data = {
            'message': key[1],
            'signature': self.sign_msg(),
            'data': key[0],
        }

        response = requests.post('https://events-api-holesky.morphl2.io/activities/open_blind_box', headers=self.headers, json=json_data)
        logger.info(response.json())
    @log('签到')  
    def sign_in(self):
        key=self.get_key()
        json_data = {
            'message': key[1],
            'signature': self.sign_msg(),
            'data': key[0],
        }

        response = requests.post('https://events-api-holesky.morphl2.io/activities/sign_in', headers=self.headers, json=json_data)
        logger.info(response.json())
    @log('投票')  
    def vote(self):
        vote=self.unused_voting_power()
        key=self.get_key(projectId='0a37c0a1-4297-4c9c-8c00-e1815cf6d993',votingPower=str(vote))
        json_data = {
            'message': key[1],
            'signature': self.sign_msg(),
            'data': key[0],
        }

        response = requests.post('https://events-api-holesky.morphl2.io/activities/vote', headers=self.headers, json=json_data)
        logger.info(response.json())
if __name__=='__main__':
    bot=Morphl2_Bot()
    # print(bot.unused_voting_power())
    print(bot.open_blind_box())
