import abc
import asyncio
from asyncio import Queue
import aiohttp

class Manager:
    """
    crawlers' manager
    """
    crawler_classes = []  #

    def __init__(self, initial_url):

        self.urls = Queue()  # urls to be consumed
        self.succeeded_urls = set() # urls that have been fetched successfully
        self.failed_urls = set()  # 抓取失败的urls
        self.initial_url = initial_url


        self.set_url_methods = []
        self.loop = asyncio.get_event_loop()



    async def manage(self):
        """

        :return:
        """
        loop = self.loop
        set_url_methods = [crawler.set_url for crawler in self.crawler_classes]
        self.set_url_methods = set_url_methods
        await self.urls.put(self.initial_url)  # initiate
        urls = self.urls
        while not urls.empty():
            async with aiohttp.ClientSession() as session: #TODO:增加UA伪造，代理IP等反反爬措施
                url = await urls.get()
                crawlers = [set_url(url) for set_url in set_url_methods]
                crawlers = [crawler.main(session) for crawler in crawlers if crawler]
                crawlers_co = asyncio.wait(crawlers)
                await crawlers_co


    def run(self):
        loop = self.loop
        loop.run_until_complete(self.manage())
        loop.close()



    def set_manager(self, crawler_class):
        self.crawler_classes.append(crawler_class)
        crawler_class.manager = self
        return crawler_class

    async def get_session(self):
        async with aiohttp.ClientSession(loop=self.loop) as session:
            self.session = session




class abcCrawler(abc.ABC):
    """
    Crawler to crawl something
    This class should be inherited by some concrete crawler classes
    Generally,just should inherit methods excluding "main"
    """
    def __init__(self, url):
        self.url = url


    @classmethod
    @abc.abstractmethod
    def isvalid_url(cls, url):
        """
        To check the url whether is valid
        :param url:
        :return: True or False
        """

    @classmethod
    def set_url(cls, url):
        if cls.isvalid_url(url):
            return cls(url)
        return None

    @abc.abstractmethod
    async def fetch(self, url, session):
        """
        To fetch the url ,and just return the raw response
        :param url:
        :return: response by fetching the url
        """
    @abc.abstractmethod
    async def parse(self, response):
        """
        Get the response,parse it
        :param response:
        :return: data: valuable and going to be stored
        """

    @abc.abstractmethod
    async def store(self, data):
        """
        Store the data to database
        :param data:
        :return: None
        """

    async def main(self, session):
        """
        The crawler's main progress,which is called by manager
        It just calls the crawler's other methods,and don't has other operations
        :return: None
        """
        try:
            url = self.url
            rep = await self.fetch(url, session)
            data = await self.parse(rep)
            await self.store(data)
        except Exception as exp:
            self.manager.failed_urls.add(self.url)
            pass
        else:
            self.manager.succeeded_urls.add(self.url)



