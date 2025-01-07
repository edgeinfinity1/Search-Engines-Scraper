import httpx
from collections import namedtuple
from .config import TIMEOUT, PROXY, USER_AGENT
from . import utils as utl


class HttpClient(object):
    '''Performs HTTP requests. A `aiohttp` wrapper, essentialy'''
    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        kwargs = {}
        if proxy:
            kwargs.update({"proxy": proxy})
        else:
            pass
        self.session = httpx.AsyncClient(**kwargs)
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-GB,en;q=0.5',
        }

        self.timeout = timeout
        self.response = namedtuple('response', ['http', 'html'])

    async def close(self):
        await self.session.aclose()

    async def get(self, page):
        '''Submits a HTTP GET request.'''
        page = self._quote(page)
        try:
            req = await self.session.get(page, headers=self.headers, timeout=self.timeout, follow_redirects=True)
            text = req.text
            self.headers['Referer'] = page
        except Exception as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=text)
    
    async def post(self, page, data):
        '''Submits a HTTP POST request.'''
        page = self._quote(page)
        try:
            req = await self.session.post(page, data=data, headers=self.headers, timeout=self.timeout, follow_redirects=True)
            text = req.text
            self.headers['Referer'] = page
        except Exception as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=text)
    
    def _quote(self, url):
        '''URL-encodes URLs.'''
        if utl.decode_bytes(utl.unquote_url(url)) == utl.decode_bytes(url):
            url = utl.quote_url(url)
        return url
    
    def _set_proxy(self, proxy):
        '''Returns HTTP or SOCKS proxies dictionary.'''
        if proxy:
            if not utl.is_url(proxy):
                raise ValueError('Invalid proxy format!')
            proxy = {'http':proxy, 'https':proxy}
        return proxy