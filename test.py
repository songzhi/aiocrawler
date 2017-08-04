import requests
import bs4
import aiocrawler.main as main

initial_url = 'http://tieba.baidu.com/p/5235802519'

manager = main.Manager(initial_url)

@manager.set_manager
class Crawler(main.abcCrawler):

    @classmethod
    def isvalid_url(cls, url):
        if url:
            return True
        return False

    def fetch(self, url):
        response = requests.get(url)
        return response

    def parse(self, response):
        resp = bs4.BeautifulSoup(response.text, 'lxml')
        title = resp.title.string
        return title

    def store(self, data):
        print(data)
        return


if __name__ == '__main__':
    manager.run()

