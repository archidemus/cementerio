import requests
import re
import urllib

class Proxies:
    def __init__(self):
        self.proxies = self.getProxies()
        self.chaingingProxies = False

    def changeProxies(self):
        if not self.chaingingProxies:
            self.chaingingProxies = True
            try:
                self.proxies = self.getProxies()
            finally:
                self.chaingingProxies = False

    def getProxies(self):
        print('Getting proxies')
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Referer': 'https://proxyscrape.com/free-proxy-list',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,es-CL;q=0.8,es;q=0.7',
        }

        params = (
            ('request', 'getproxies'),
            ('proxytype', 'http'),
            ('timeout', '10000'),
            ('country', 'CL'),
            ('ssl', 'all'),
            ('anonymity', 'all'),
        )

        response = str(requests.get('https://api.proxyscrape.com/', headers=headers, params=params).content)
        proxies = re.findall(r'((?:\d{1,3}\.){3}\d{1,3}:\d+)', response)
        print('Testing proxies')
        for proxy in proxies:
            if not self.proxyOk(proxy):
                proxies.remove(proxy)
        return proxies

    def proxyOk(self, proxy):
        try:
            requests.get('http://example.org/', proxies={'http': proxy, 'https': proxy}, timeout=4)
            return True
        except:
            return False