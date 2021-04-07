import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from berkshirebank.items import Article


class berkshirebankSpider(scrapy.Spider):
    name = 'berkshirebank'
    start_urls = ['https://www.berkshirebank.com/About/Whats-New/News-Media/Press-and-Media-Releases-20-21',
                  'https://www.berkshirebank.com/About/Whats-New/News-Media/Archived-Press-and-Media-Releases-2015-2019']

    def parse(self, response):
        articles = response.xpath('//main//ul[@class="list-unstyled"]/li/a')
        for article in articles:
            link = article.xpath('./@href').get()
            date = article.xpath('./text()').get()
            if date:
                date = date.split()[0]

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@id="MainContent"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
