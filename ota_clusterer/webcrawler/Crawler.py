#!/usr/bin/env python

__author__ = 'Sandro Cilurzo'

import csv
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from ota_clusterer import settings
from ota_clusterer import logger
from ota_clusterer.webcrawler.spiders.WebCrawlingSpider import WebCrawlingSpider
import ota_clusterer.webcrawler.settings as scrapy_settings



logger = logger.get_logger()
logger.name = __name__


class Crawler:
    """Class for Web Crawling

    Uses Scrapy as web crawling framework to spawn multiple crawling spiders (for each given hostname).
    Hostnames can come from a list object, [www.test.ch, www.test2.de] or a csv file with newline seperated entries.
    """

    def get_hostnames_from_csv_list(self, csv_file_path):
        """read csv and extract urls
        :param csv_file_path: where the csv is stored
        :return: list [], of hostnames

        """

        hostnames = []
        with open(csv_file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                hostname = row[0].replace('http://www.', '')
                hostname = hostname.replace('https://www.', '')
                hostname = hostname.strip('/')
                hostnames.append(hostname)

        return hostnames

    def crawl_hostnames(self, hostnames, directory_to_save_results):
        """perform crawling for given hostnames and persist results
        :param hostnames: list [], of hostnames to crawl
        :param directory_to_save_results: where to store the crawled results

        """

        configure_logging()
        runner = CrawlerRunner(get_project_settings())
        for hostname in hostnames:
            runner.crawl(WebCrawlingSpider,
                         hostname=hostname,
                         start_urls=['http://' + hostname, 'https://' + hostname],
                         directory_path_to_save_results=directory_to_save_results)
            d = runner.join()
            d.addBoth(lambda _: reactor.stop())
        reactor.run()

    def ignore_robotstxt_file(self):
        """ enable 'ignore robots.txt' file in crawler

        """

        scrapy_settings.ROBOTSTXT_OBEY = False


def crawl_given_hostnames(hostnames, directory_to_save_results):
    """helper class to crawl given urls
    :param hostnames: urls to crawl
    :param directory_to_save_results: where to persist the result

    """

    crawler = Crawler()
    logger.info('crawl following urls (hostnames): ' + str(hostnames))
    crawler.crawl_hostnames(hostnames, directory_to_save_results)


def crawl_list_of_hostnames(urls_list_file_path, directory_to_save_results):
    """ helper class to crawl list of hostnames

    :param urls_list_file_path:
    :param directory_to_save_results:
    :return:
    """
    crawler = Crawler()
    logger.info('crawl following list of urls: ' + urls_list_file_path)
    hostnames = crawler.get_hostnames_from_csv_list(urls_list_file_path)
    crawler.crawl_hostnames(hostnames, directory_to_save_results)


def main():
    # Example to crawl just specific urls
    directory_to_save_results = settings.DATA_DIR + 'experiments/crawling_data_experiments/'
    hostnames = ['upkbs.ch', 'curaneo.ch', 'bscyb.ch', 'scltigers.ch', 'graubuenden.ch']
    crawl_given_hostnames(hostnames, directory_to_save_results)

    '''
    # Example to crawl list of urls
    urls_list = settings.DATA_DIR + 'urls/urls-to-crawl.csv'
    directory_to_save_results = settings.DATA_DIR + 'experiments/crawling_data_experiments/'
    crawl_list_of_hostnames(urls_list, directory_to_save_results)
    
    '''


if __name__ == "__main__":
    main()
