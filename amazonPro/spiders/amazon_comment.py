from scrapy_redis.spiders import RedisSpider


class Amazon_CommentSpider(RedisSpider):
    name = "amazon_comment"
    # allowed_domains = ["xx"]
    # start_urls = ["http://xx/"]
    redis_key = 'amazon_comment'  # 可以被共享的调度器队列名称

    def parse(self, response):
        pass