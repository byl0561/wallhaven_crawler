import hashlib
import os
import re
import time
import urllib.parse
import urllib.request


def img_download(img_url: str, work_dir: str, exist_file_md5: list[str]):
    raw_data = http_get(img_url, decode=False)
    file_name = get_image_absolute_location(work_dir, img_url)
    md5 = hashlib.md5(raw_data).hexdigest()
    if md5 not in exist_file_md5:
        with open(file_name, 'wb') as f:
            f.write(raw_data)


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


def find_all_file(dir: str):
    for root, ds, fs in os.walk(dir):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def collct_exist_image_md5(dir: str) -> set[str]:
    exist_file_md5 = set()
    for file_name in find_all_file(dir):
        with open(file_name, 'rb') as fp:
            data = fp.read()
        file_md5 = hashlib.md5(data).hexdigest()
        exist_file_md5.add(file_md5)
    return exist_file_md5


def get_image_absolute_location(work_dir: str, img_url: str) -> str:
    file_name = img_url[img_url.rfind('-') + 1:]
    file_name = work_dir + '/' + file_name
    return file_name


def crawling_img_url_list_form_homepage(page_content: str) -> list[str]:
    lt = re.findall(r'<li><figure.*?>.*?<a class="preview" href="(.*?)" .*?></a>.*?</figure></li>', page_content, flags=re.S)
    img_url_list = list()
    for img_page_src in lt:
        resp = http_get(img_page_src)
        img_url_matched = re.findall(r'<section id="showcase".*?>.*?<div.*?>.*?<img id="wallpaper" src="(.*?)" .*?>.*?</a>.*?</div></section>', resp, flags=re.S)
        img_url_list.append(img_url_matched[0])
        time.sleep(1)
    return img_url_list


def main():
    homepage_url = 'https://wallhaven.cc/toplist'
    work_dir = './wallhaven'
    cmp_dir = '/Volumes/Picture'

    print("*" * 8, "wallhaven壁纸批量下载", "*" * 8)

    page_start = int(input("请输入开始页码:"))
    page_end = int(input("请输入结束页码:"))

    print("已有数据加载中...")
    exist_file_md5 = collct_exist_image_md5(cmp_dir)

    for page in range(page_start, page_end + 1):
        print("开始传输第%s页数据" % page)
        page_content = http_get(homepage_url, param={"page": page})
        img_url_list = crawling_img_url_list_form_homepage(page_content)
        for img_url in img_url_list:
            img_download(img_url, work_dir, exist_file_md5)
            time.sleep(10)


if __name__ == "__main__":
    main()
