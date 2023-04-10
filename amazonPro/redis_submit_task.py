import json
from redis import StrictRedis
from amazonPro import settings




def get_param(url,method):
    if '?' in url:
        url_str = url.split('?',1)[0]
        url_end = url.split('?',1)[1]
        key_value_list = url_end.split('&')
        meta_dic = {}
        for item in key_value_list:
            key_str = item.split('=')[0]
            value_str = item.split('=')[1]
            meta_dic[key_str] = value_str
        params = dict(
            url=url_str,
            method=method,
            meta=meta_dic
        )
        return params
    else:
        meta_dic = {}
        params = dict(
            url=url,
            method=method,
            meta=meta_dic
        )
        return params


def submit_redis_url(redis_key,method,url):
    with StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
    ) as redis_client:
        # params = dict(
        #     url='https://movie.douban.com/top250',
        #     method='GET',
        #     meta={'key1': 'v1', 'key2': 'v2'}
        # )

        # params = dict(
        #     url=url,
        #     method=method,
        #     meta=meta
        # )
        params = get_param(url,method)
        redis_client.lpush(redis_key, json.dumps(params))
        redis_client.close()



# submit_redis_url('amazon_detail', 'GET', 'https://www.amazon.de/dp/B004SBB6UA/ref=sr_1_1_sspa')
