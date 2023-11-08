import hashlib
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error

dirname = './wallhaven'
basename = '/Volumes/Picture'


def img_download(countent, excluded_file):
    lt = re.findall(r'<li><figure.*?>.*?<a class="preview" href="(.*?)" .*?></a>.*?</figure></li>', countent,
                    flags=re.S)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    for img_src in lt:
        resp = http_get(img_src)
        full_src = re.findall(r'<section id="showcase".*?>.*?<div.*?>.*?<img id="wallpaper" src="(.*?)" .*?>.*?</a>.*?</div></section>', resp,
                        flags=re.S)[0]

        file_name = full_src[full_src.rfind('-') + 1:]
        file_name = dirname + '/' + file_name
        try:
            raw_data = http_get(full_src, decode=False)
            print("%s开始下载" % file_name)
            md5 = hashlib.md5(raw_data).hexdigest()
            if md5 not in excluded_file:
                with open(file_name, 'wb') as f:
                    f.write(raw_data)
                print("%s下载完成" % file_name)
            else:
                print("%s重复，已过滤" % file_name)
        except urllib.error.HTTPError as e:
            print(f'{img_src} - {e}')


def http_get(url: str, param: dict = None, decode: bool = True):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    }
    if param is not None:
        url += "?"
        for k, v in param.items():
            url += k + "=" + str(v)

    request = urllib.request.Request(url=url, headers=headers)
    response_raw = urllib.request.urlopen(request).read()
    if decode:
        return response_raw.decode()
    else:
        return response_raw


def request_get(url, headers, page):
    page_url = url + str(page)
    request = urllib.request.Request(url=page_url, headers=headers)
    return request


def find_all_file():
    for root, ds, fs in os.walk(basename):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def main():
    print("*" * 8, "wallhaven壁纸批量下载", "*" * 8)
    page_start = int(input("请输入开始页码:"))
    page_end = int(input("请输入结束页码:"))
    homepage_url = 'https://wallhaven.cc/toplist'

    print("已有数据加载中...")
    exist_file_md5 = set()
    for file_name in find_all_file():
        with open(file_name, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()
        exist_file_md5.add(file_md5)

    for page in range(page_start, page_end + 1):
        print("开始传输第%s页数据" % page)
        content = http_get(homepage_url, param={"page": page})
        img_download(content, exist_file_md5)
        print("第%s页数据传输完成" % page)
        print()
        print()
        time.sleep(30)


if __name__ == "__main__":
    main()
