import abc


class Manager:
    """
    crawlers' manager
    """
    crawler_classes = []  #

    def __init__(self, initial_url):

        self.urls = set()  # urls to be consumed
        self.succeeded_urls = set() # urls that have been fetched successfully
        self.failed_urls = set()  # 抓取失败的urls

        self.urls.add(initial_url)  # initiate
        self.set_url_methods = []


    def run(self):
        """

        :return:
        """
        set_url_methods = [crawler.set_url for crawler in self.crawler_classes]
        self.set_url_methods = set_url_methods
        urls = self.urls
        while urls:
            url = urls.pop()
            crawlers = [set_url(url) for set_url in set_url_methods]
            crawlers = [crawler for crawler in crawlers if crawler]
            for crawler in crawlers:
                crawler.main()

    def set_manager(self, crawler_class):
        self.crawler_classes.append(crawler_class)
        crawler_class.manager = self
        return crawler_class




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
    def fetch(self, url):
        """
        To fetch the url ,and just return the raw response
        :param url:
        :return: response by fetching the url
        """
    @abc.abstractmethod
    def parse(self, response):
        """
        Get the response,parse it
        :param response:
        :return: data: valuable and going to be stored
        """

    @abc.abstractmethod
    def store(self, data):
        """
        Store the data to database
        :param data:
        :return: None
        """

    def main(self):
        """
        The crawler's main progress,which is called by manager
        It just calls the crawler's other methods,and don't has other operations
        :return: None
        """
        try:
            url = self.url
            rep = self.fetch(url)
            data = self.parse(rep)
            self.store(data)
        except Exception as exp:
            self.manager.failed_urls.add(self.url)
            pass
        else:
            self.manager.succeeded_urls.add(self.url)



