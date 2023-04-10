from selenium import webdriver
from amazonPro import config
import time
import random
import requests
import sys

@staticmethod
def get_chrome_start_args(local, headless, css, img, proxy,user_data_dir=config.CHROME_DATA_PATH_LOCAL):
    options = webdriver.ChromeOptions()
    chrome_conf = [
        '--ignore-certificate-error',   # 忽略证书认证出错
        '--ignore-ssl-errors',  # 忽略ssl出错
        '--no-sandbox',  # 禁止沙箱运行，解决linux无头无法运行
        # 'lang=en_us.UTF-8',
        '--disable-dev-shm-usage',  # 解决linux无头无法运行
        # '--disable-software-rasterizer',   # 禁用浏览器GL锁
        # '--user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"',
        '--disable-popup-blocking',  # 禁用弹出拦截
        '--disable-infobars',   # 禁止出现浏览器被控制
        '--ignore-certificate-errors',  # 忽略私密链接
    ]
    '''# 不开启无头，就开启无痕，（linux自动开启无头模式，无痕模式只有windows环境下启用）'''
    if proxy:
        res = requests.get("http://thomas.suncentgroup.com/api/thomas_proxy/").json()
        chrome_conf.append(f'--proxy-server={res.get("host")}:{res.get("port")}')
    if headless or 'linux' == sys.platform:chrome_conf.append('--headless')
    elif not local and 'win32' == sys.platform: chrome_conf.append('--incognito')
    '''# 只有windows环境下才能开启本地缓存'''
    if local and 'win32' == sys.platform: chrome_conf.append(f'user-data-dir={user_data_dir}')
    '''windows环境下自动禁用GPU'''
    for i in chrome_conf:options.add_argument(i)
    prefs = {
        'profile.managed_default_content_settings.images': 2,   # 禁止加载图片
        'permissions.default.stylesheet': 2,    # 禁止加载css
        'useAutomationExtension': False,    # 屏蔽自动化
        'directory_upgrade': True,
        'profile.default_content_setting_values': {'notifications': 2},
        'profile.default_content_settings.popups': 0,  # 防止下载保存弹窗
        'download.default_directory': config.DOWNLOAD_PATH,  # 设置默认下载路径
        "profile.default_content_setting_values.automatic_downloads": 1,    # 禁止下载文件弹窗
        'safebrowsing.enabled': False,  # 安全模式
    }
    if css:del prefs['permissions.default.stylesheet']
    if img:del prefs['profile.managed_default_content_settings.images']
    options.add_experimental_option("useAutomationExtension", False)  # 防止检测无头屏蔽自动化控制
    options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 防止检测无头屏蔽自动化控制
    options.add_experimental_option('prefs', prefs)  # 禁用浏览器弹窗
    # options.add_experimental_option('detach', True)       #浏览器不重启
    if config.IS_SELENIUM_LOGGING:
        options.add_experimental_option('excludeSwitches', ['enable-logging'])   #关闭selenium打印日志
    return options

@staticmethod
def get_driver(local=False, headless=False, css=True, img=True, proxy=False):
    options = get_chrome_start_args(local, headless, css, img, proxy)
    driver = webdriver.Chrome(executable_path=config.CHROME_EXECUTABLE_PATH, options=options)
    driver.execute_cdp_cmd("Network.enable", {})

    script_ls = [
        '''Object.defineProperty(navigator, 'webdriver', {get: () => undefined})''',
        '''window.navigator.chrome = {runtime: {},// etc.};''',
        # '''Object.defineProperty(navigator, 'plugins', {get: () => [5,4514,sfsded],});''',
        # '''Object.defineProperty(navigator, 'languages', {get: () => ['en', 'zh', 'und'],});''',
    ]
    for script in script_ls:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
    driver.maximize_window()
    driver.implicitly_wait(1)
    driver.set_page_load_timeout(40)  # 全局请求页面超时时间
    driver.set_script_timeout(40)  # 全局请求页面js加载超时时间
    print('浏览器加载完毕')
    time.sleep(random.uniform(1, 2))
    return driver