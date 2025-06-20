# scrapHelper.py
import random
import requests
from urllib.parse import urlparse
from requests.exceptions import RequestException


USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",

    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",

    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",

    # Mobile
    "Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.70 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

PROXIES = [
    "http://154.65.39.7:80",
    "http://159.203.61.169:3128",
    "http://158.255.77.169:80",
    "http://219.65.73.81:80",
    "http://91.103.120.39:80",
    "http://57.129.81.201:8080",
    "http://51.81.245.3:17981",
    "http://32.223.6.94:80",
    "http://159.65.245.255:80",
    "http://47.236.224.32:8080",
    "http://14.241.80.37:8080",
    "http://190.58.248.86:80",
    "http://50.122.86.118:80",
    "http://66.191.31.158:80",
    "http://98.191.238.177:80",
    "http://200.255.88.23:80",
    "http://103.154.87.12:80",
    "http://91.103.120.37:80",
    "http://185.234.65.66:1080",
    "http://91.103.120.40:80",
    "http://156.38.112.11:80",
    "http://198.23.143.74:80",
    "http://81.169.213.169:8888",
    "http://23.247.136.254:80",
    "http://188.166.197.129:3128",
    "http://91.103.120.57:80"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_random_proxy():
    return None

def apply_scrape_options(options, proxy=None, user_agent=None):
    # Set User-Agent
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

    # Set proxy if provided
    if proxy:
        print(f"🌐 Using proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")

    # Prevent detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Headless mode is currently disabled to allow manual inspection
    # To enable headless, uncomment the following line:
    # options.add_argument("--headless=new")

    return options

def test_proxy_connectivity(proxy_url, test_url="https://www.ebay.com"):
    """
    Attempts to make a test request through the proxy.
    Returns True if successful, False if connection fails.
    """
    print(f"🌐 Testing proxy: {proxy_url}")
    parsed = urlparse(proxy_url)
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=8)
        if response.status_code == 200:
            print("✅ Proxy test passed")
            return True
        else:
            print(f"⚠️ Proxy responded with status: {response.status_code}")
            return False
    except RequestException as e:
        print(f"❌ Proxy error (bad gateway or unsupported): {proxy_url} -> {e}")
        return False