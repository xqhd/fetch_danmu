from curl_cffi import requests
from typing import Dict, List
from tqdm import tqdm


def read_proxies() -> List[str]:
    proxies = []
    with open("proxies.csv", "r") as f:
        for line in f:
            if line.startswith("ip"):
                continue
            ip, port = line.strip("\n").split(",")
            proxies.append(f"http://{ip}:{port}")
    return proxies


# 测试代理是否可用的函数
def test_proxy(proxy: Dict[str, str]) -> bool:
    test_url = "https://openapi.973973.xyz/open/api_free/index/?pltfrom=5010&url=https://v.qq.com/x/cover/mzc00200fboxu3c/f41012jwko1.html"  # 测试 URL，返回当前 IP
    try:
        response = requests.get(
            test_url, proxy=proxy, timeout=500, impersonate="chrome124", verify=False
        )
        if response.status_code == 200:
            print(f"Proxy {proxy} is working. Response: {response.text}")
    except Exception as _:
        pass


def main():
    proxies = read_proxies()
    for proxy in tqdm(proxies):
        test_proxy(proxy)


if __name__ == "__main__":
    main()
