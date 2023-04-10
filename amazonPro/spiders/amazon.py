import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


import time
from amazonPro import config
from scrapy_redis.spiders import RedisSpider
from amazonPro.redis_submit_task import submit_redis_url
from amazonPro.webdriver_start_parmas import get_driver
from lxml import etree
class AmazonSpider(RedisSpider):

    '''
    1.根据关键词  查看自家asin的排名   广告排名  非广告排名  spons这个就是广告
    2.根据asin链接   详情页qa及评论数据
    提交  qa跟详情页的 yield
    3.查到跟买   钉钉报警   差评通知
    4.物流 - 跨境物流 17TK

    '''

    name = "amazon"
    # allowed_domains = ["xx"]
    # start_urls = ["http://xx/"]
    redis_key = 'amazon_detail'  # 可以被共享的调度器队列名称
    is_first = True
    def __init__(self):
        self.bro = get_driver()

        submit_redis_url(self.redis_key, 'GET', 'https://www.amazon.com/dp/B00PGXQ68Q/ref=sr_1_1_sspa')    #不理解放在这里就可以正常，放在上面就会执行两次，为什么？

    def parse(self, response,**kwargs):
        '''
        主图
        评论数
        qa数量
        '''

        html = etree.HTML(response.text)
        set_postal_code(config.POST_CODE, html)

        data = {}
        data['image'] = html.xpath("//*[contains(@class,'imgTagWrapper')]/img/@src")[0]  #主图
        ratings = html.xpath('//*[@id="acrCustomerReviewText"]/text()')
        if ratings:data['ratings'] = ratings[0]   #评论数
        answered_questions = html.xpath('//*[@id="askATFLink"]/span/text()')
        if answered_questions : data['answered_questions'] = answered_questions[0] #qa数量
        brand = html.xpath('//*[@id="bylineInfo"]/text()')
        if brand : data['brand'] = brand[0]                   #跟卖链接
        star_avg = html.xpath(
            '//*[@id="reviewsMedley"]//div[@class="a-row"]/span[@class="a-size-base a-nowrap"]/span[@data-hook="rating-out-of-text"]/text()')
        if star_avg :data['star_avg'] = star_avg[0]
        star_k = html.xpath('//tr[@class="a-histogram-row a-align-center" or @class="a-histogram-row"]/text()') #星评
        star_v = html.xpath('//table[@id="histogramTable"]/tbody/tr/td[3]/text()')
        comment_url = html.xpath('//*[@id="reviews-medley-footer"]/div[2]/a/@href')
        if comment_url : data['comment_url'] = comment_url
        qa_url = html.xpath('//*[@class ="a-button a-button-base askSeeMoreQuestionsLink"]/span/a/@href')
        if qa_url: data['qa_url'] = qa_url
        qa_detail_url = html.xpath('//a[@class="a-link-normal askWidgetSeeAllAnswersInline"]')





        print(data)
        yield data
        # if config.IS_GET_QA:
        #     ''' 3种情况，1中是qa很多需要打开qa列表页，先跳到列表页，再进行qa爬取。   第二种是没有qa列表页，但是有qa，需要爬qa  第三种
        #     情况没有qa     这些有的要跳转qa列表，有的要跳转详情'''
        #     if qa_url:
        #         submit_redis_url('qa_list', 'GET', "https://www.amazon.com"+qa_url)
        #     elif qa_detail_url:
        #         for qa in qa_detail_url:
        #             submit_redis_url('qa_detail', 'GET', "https://www.amazon.com" + qa.xpath('./@href'))
        #
        # elif config.IS_GET_COMMENT:
        #     pass
            # submit_redis_url(self.redis_key, 'GET', 'https://www.amazon.de/dp/B004SBB6UA/ref=sr_1_1_sspa')



# https://www.amazon.com/Premade-Easter-Baskets-Adults-Filled/dp/B07Q3WFK8H/ref=sr_1_1_sspa             #详情页链接
# https://www.amazon.com/Premade-Easter-Baskets-Adults-Filled/product-reviews/B07Q3WFK8H/ref=cm_cr_dp_d_show_all_btm        评论链接
def click_element():
    '''检查元素是否出现，出现就点击'''
    pass

def choose_localtion():
    #设置地区
    pass


def get_asin_id_from_url(url):
    pass
def set_postal_code(post_code,html):
    '''
    设置邮编   检查是否有设置的按钮，有的话点击按钮设置，没有就报错 成功了刷新页面返回1，失败了返回no
    :param post_code: 邮编   html 响应数据
    :return: bool 失败成功
    '''
    wait()



def wait(self, key, value, time_out: float = 20, error='元素加载超时', element=None, s_sleep=0.0):

    '''
    key 元素方式
    value 元素xpath路径
    return 是否找到
    '''
    if s_sleep > 0:
        time.sleep(s_sleep)
    if not element: element = self.driver
    if not key:
        try:
            return element.find_element(By.XPATH, value)
        except:
            print(f'等待超时>{key}=\'{value}\'  {error}')
            return None
    else:
        try:
            selector = {
                'id': By.ID,
                'xpath': By.XPATH,
                'text': By.LINK_TEXT,
                'name': By.NAME,
                'css': By.CSS_SELECTOR,
                'tag': By.TAG_NAME,
                'class': By.CLASS_NAME,
            }
            return WebDriverWait(element, time_out, 0.3).until(
                EC.element_to_be_clickable((selector[key], value)))
        except:
            print(f'等待超时>{key}=\'{value}\'  {error}')
            return None

# def make_url_by_asin_id(asin_id,url,make_type):
#     #1详情页链接 2评论链接 3qa链接
#     pass
#
#
#
#     def click(self, element, text=None, async_script=False, js=True, sleep=0.0, s_sleep=0.0):
#         try:
#             name = element.text
#         except:
#             name = '未知'
#         try:
#             if not element:
#                 print('element为空')
#                 return
#             elif not text or text in element.text:  # 判断条件成立可以进行写入操作
#                 time.sleep(random.uniform(s_sleep, s_sleep + 0.2))
#                 if js and async_script:  # 判断条件成立使用异步JS进行写入
#                     self.driver.execute_async_script("arguments[0].click();", element)
#                 elif js:
#                     self.driver.execute_script("arguments[0].click();", element)
#                 else:
#                     element.click()
#                 print(f'点击>{text or name}')
#                 time.sleep(random.uniform(sleep, sleep + 1))
#             else:
#                 print(f'点击>目标元素中不存在text：{text},{Exception}')
#         except Exception as e:
#             print(f'点击未知错误>{text or name}  {e}')
#
#     def write(self, element: WebElement, value, name=None, attr='value', js=True, sleep=0.0):
#         # try:
#         if js:
#             self.driver.execute_script(f'arguments[0].{attr}="{value}";', element)
#         else:
#             element.clear()
#             element.send_keys(value)
#         print(f'填写>{name or ""}:{value}')
#         if sleep > 0:
#             time.sleep(random.uniform(sleep, sleep + 2))
#         # except Exception as e:
#         #     print(f'填写>{name or ""}:{value}   {e}')
#
#     def read(self, element, name=None, attr='textContent', js=True, s_sleep=0.0):
#         if s_sleep > 0: time.sleep(s_sleep)
#         try:
#             if not element:
#                 print('读取element为空')
#                 return ''
#             elif js:
#                 temp = self.driver.execute_script(f"return arguments[0].{attr};", element)
#             else:
#                 temp = element.get_attribute(attr)
#             print(f'读取>{name or attr}:{temp.split() or ""}')
#             return temp
#         except Exception as e:
#             print(f'读取>{name or attr}        {e}')
#             return ''
#
#     def iframe(self, iframe=None, out_time=20):
#         try:
#             if iframe == '上一层':
#                 self.driver.switch_to.parent_frame()
#             elif isinstance(iframe, int):
#                 iframe = self.driver.find_elements_by_tag_name('iframe')[iframe]
#                 WebDriverWait(self.driver, out_time, 0.5).until(EC.frame_to_be_available_and_switch_to_it(iframe))
#             elif iframe:
#                 WebDriverWait(self.driver, out_time, 0.5).until(EC.frame_to_be_available_and_switch_to_it(iframe))
#             else:
#                 self.driver.switch_to.default_content()
#             print(f'切换iframe>{iframe or "default"}')
#         except Exception as e:
#             print(f'切换iframe>{iframe or "default"}')
#
#     def windows(self, tab, sleep=0.0):
#         time.sleep(random.uniform(0.5, 1))
#         try:
#             if isinstance(tab, int):
#                 self.driver.switch_to.window(self.driver.window_handles[tab])
#                 if sleep > 0:
#                     time.sleep(random.uniform(sleep, sleep + 2))
#                 print(f'切换windows> {tab} 的窗口')
#             elif isinstance(tab, str):
#                 for handle in self.driver.window_handles:
#                     self.driver.switch_to.window(handle)
#                     if tab in self.driver.title:
#                         print(f'切换windows> {tab} 的窗口')
#                         if sleep > 0:
#                             time.sleep(random.uniform(sleep, sleep + 2))
#                         break
#         except Exception as e:
#             print(f'切换windows> {tab} 的窗口')
#
#     def get(self, url, sleep=0.0, first=True):
#         try:
#             print(f'请求> {url}')
#             self.driver.get(url)
#             if sleep > 0:
#                 time.sleep(random.uniform(sleep, sleep + 2))
#         except:
#             # if sleep > 0:
#             #     time.sleep(random.uniform(sleep, sleep + 2))
#             print(f'请求>超时:{url}')
#             try:
#                 self.driver.execute_script('window.stop()')
#             except:
#                 pass
#             if first:
#                 self.get(url, sleep, False)
#             elif self.driver.current_url in url:
#                 return
#             else:
#                 raise ValueError(f'请求超时：{url}')
#
#     def get_new_window(self, url, tab=None):
#         if not tab:
#             tab = -1
#         self.driver.execute_script(f'window.open("{url}")')
#         print(f'请求>{url}')
#         self.windows(tab)
#
#     def do_language_unification(self, language='English'):
#         map_lang = {
#             'English': 'en',
#             '中文': 'zh',
#         }
#         new_language = self.read(self.wait('xpath', tally['后台_当前语言']), js=False)
#         if not new_language:
#             return
#         elif language in new_language:
#             print(f'切换{language}成功')
#         else:
#             try:
#                 selector = Select(self.driver.find_element_by_xpath(tally['后台_切换语言选择器']))
#                 print(f'语言切换:{language}')
#                 selector.select_by_visible_text(language)
#                 time.sleep(random.uniform(8, 10))
#             except:
#                 try:
#                     if language not in self.read(self.wait('xpath', tally['后台_当前语言']), js=False):  # 新模式
#                         ActionChains(self.driver).move_to_element(self.wait('class', 'locale-icon-wrapper', 0)).pause(
#                             random.uniform(1, 2)).click(self.wait('xpath',
#                                                                   f'//*[@class="localeListRoot"]//label/input[starts-with(@value,"{map_lang[language]}_")]',
#                                                                   0)).pause(random.uniform(5, 8)).perform()
#                 except Exception as e:
#                     print(e)
#         return self.wait('xpath', tally['后台_当前语言'])
#
#     def do_switch_site_move_selector(self):
#         try:
#             element = self.wait('xpath', tally['后台_切换站点选择器'], random.uniform(10, 15), s_sleep=random.uniform(0.5, 1))
#             o = ActionChains(self.driver)
#             o.move_to_element(element)
#             # o.click(element)
#             # o.move_to_element(element)
#             o.pause(random.uniform(2, 3))
#             o.perform()
#         except Exception as e:
#             print(e)
#             pass
#         return self.read(self.wait('xpath', '//*[@class="currentSelection"]', time_out=random.uniform(3, 5)),
#                          attr='id') or self.etree_return(etree.HTML(self.driver.page_source),
#                                                          '//*[@class="currentSelection"]/@id')
#
#     def do_switch_site_get(self, host):
#         self.get(f'https://{host}/home{random.choice(["?", "/?"])}', sleep=random.uniform(3, 5))
#         self.do_login()
#         # spik_all_element = self.wait('xpath', '//*[@data-test-tag="secondary-action"]', 0)
#         # if spik_all_element: self.click(spik_all_element, js=False)
#         return self.do_switch_site_move_selector()
#
#     def do_switch_site(self, marketplace_id, lang='English'):
#         flag_site = getattr(CrlDict.objects.get(dict_code='site_code', marketplace_id)
#         host = getattr(CrlDict.objects.get(dict_code="backend_host"), marketplace_id)
#         print(f'开始切换站点：{flag_site}')
#         if 'sellercentral' not in self.driver.current_url or '/home' not in self.driver.current_url: self.do_switch_site_get(
#             host)
#         if self.wait('xpath', tally['登录_打勾'], time_out=random.uniform(2, 4)): self.do_login()
#         if not self.wait('xpath', tally['后台_切换站点选择器'], random.uniform(15, 20)):
#             return
#         site = self.do_switch_site_move_selector()
#         if not site: return  # 未登录
#         if site == marketplace_id and not self.wait('xpath',
#                                                     '//a[contains(@href,"/ref=xx_sitemetric_foot_xx")]|//a[contains(@href,"/ref=xx_invmgr_foot_xx")]',
#                                                     0):
#             self.click(self.wait('xpath', tally['logo']), js=False, sleep=random.uniform(6, 8))
#         elif site and site != marketplace_id:
#             self.do_switch_site_get(host)
#             self.click(self.wait('xpath', f'//a[@id="{marketplace_id}"]', random.uniform(1, 3)), js=False,
#                        sleep=random.uniform(8, 12))
#         return self.do_language_unification(lang)
#
#     def get_amazon_data(self):
#         '''获取seller_id（A2RWGKKYBI1NH）和站点'''
#         time.sleep(5)
#         temp_data = re.findall('<script id=\"spaui-state\".*?\{\n(.*?)\}', self.driver.page_source, re.S)
#         if temp_data:
#             seller_id = temp_data[0].replace('\n', '').replace(' ', '').replace('\"', '')
#             for i in seller_id.split(','):
#                 i = i.split(':')
#                 self.amazon_data[i[0]] = i[1]
#
#     def plugin_scrollbar(self, element, sleep: float = 0):
#         '''
#         滚动条
#         顶部：element = 1
#         底部：element = 'document.body.scrollHeight'
#         数值：高度数值
#         element = 标签
#         '''
#         time.sleep(sleep)
#         if isinstance(element, str) or isinstance(element, int):
#             self.driver.execute_script(f'window.scrollTo(1,{element});')
#         elif element:
#             self.driver.execute_script("arguments[0].scrollIntoView();", element)
#
#     def date_coord(self, date: datetime.date, init_date=datetime.date.today(), sunday_first=False):
#         '''日期坐标   默认sunday_first=False以周一-周日为1-7，sunday_first=True以周日-周六为1-7'''
#         weekday = date.isoweekday()  # 星期几（1-7）
#         week_num = int(date.strftime('%W')) - int(date.replace(day=1).strftime('%W')) + 1
#         x_move = date.month - init_date.month + (date.year - init_date.year) * 12
#         if sunday_first:
#             if weekday == 7:
#                 weekday, week_num = 1, week_num + 1
#             else:
#                 weekday += 1
#         data = {
#             'x': weekday,
#             'y': week_num,
#             'move': x_move,
#         }
#         return data
#
#     def select_performance_date(self, xy: dict, index=0):
#         '''因为周日是1  周六是7  处理xy'''
#         start_element = self.driver.find_elements_by_tag_name('kat-date-picker')[index]
#         self.click(start_element, js=False, sleep=random.uniform(1, 2))
#         if xy.get('move') != 0:
#             if xy.get('move') < 0:
#                 t = 'cal-lft'
#             else:
#                 t = 'cal-rgt'
#             move_element = self.get_shadow(self.get_shadow(start_element, index=1)).find_element_by_xpath(
#                 f'.//button[@class="{t}"]')
#             for i in range(abs(xy.get('move'))):
#                 self.click(move_element, js=False, s_sleep=random.uniform(1, 1.5), sleep=random.uniform(1, 1.5))
#         self.click(self.get_shadow(self.get_shadow(start_element, index=1)).find_element_by_xpath(
#             f'.//tbody/tr[{xy.get("y")}]/td[{xy.get("x")}]/button'), s_sleep=random.uniform(1, 2),
#                    sleep=random.uniform(2, 4))
#
#     def action_chains_input(self, element, value, element_subjoin=None):
#         action_chains = ActionChains(self.driver)
#         action_chains.move_to_element(element)
#         action_chains.click(element)
#         action_chains.pause(random.uniform(2, 3))
#         action_chains.send_keys(Keys.END)
#         for i in range(random.randint(11, 13)):
#             action_chains.send_keys(Keys.BACKSPACE)
#         action_chains.pause(random.uniform(1, 2))
#         action_chains.send_keys(value)
#         if element_subjoin:
#             action_chains.pause(random.uniform(1, 2))
#             action_chains.click(element_subjoin)
#         action_chains.perform()
#
#         def click_to_disappear(self, xpath, time_out: float, click_number: int):
#             '''如果有该xpath，点击click_number次，点击到元素消失'''
#             for i in range(click_number):
#                 temp = self.wait('xpath', xpath, s_sleep=random.uniform(time_out - 3, time_out + 3),
#                                  time_out=random.uniform(2, 5))
#                 if temp:
#                     self.click(temp, js=False)
#                     if not self.wait('xpath', xpath, time_out=0, s_sleep=random.uniform(2, 4)):
#                         return
#                 else:
#                     return
#             self.driver.refresh()
#             time.sleep(15)
#
#         def wait_loading(self, xpath, time_out=15):
#             time.sleep(random.uniform(3, 5))
#             for j in range(time_out):
#                 if self.wait('xpath', xpath, time_out=0):
#                     time.sleep(1)
#                 else:
#                     print(f'该loading已消失 {xpath}')
#                     return False
#             try:
#                 self.driver.refresh()
#             except:
#                 pass
#             time.sleep(random.uniform(time_out, time_out + 2))
#             return True
#
#         @staticmethod
#         def etree_return(element, xpath, _list=False):
#             if not _list:
#                 try:
#                     return element.xpath(xpath)[0]
#                 except:
#                     return ''
#             else:
#                 try:
#                     return element.xpath(xpath)
#                 except:
#                     return ''
#
#         @staticmethod
#         def object_is_type(obj, _type):
#             try:
#                 return _type(obj)
#             except:
#                 return False