import sys
import requests
import re
import argparse


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="targ_url", help="Type an url you want to crawl")
    parser.add_argument("--internal", help="Crawl only internal links on the page except of relative links",
                        action="store_true")
    parser.add_argument("--external", help="Crawl only external links", action="store_true")
    parser.add_argument("--relative", help="Crawl only relative links", action="store_true")
    options = parser.parse_args()
    if not options.targ_url:
        parser.error("\033[0;31m[-] \033[0;33mPls specify an url")
    else:
        return options


def t_url_strip(raw_url):  # Скармливаем любые ссылки с http или https
    if "https://" in raw_url:
        raw_url = raw_url[8:]
    elif "http://" in raw_url:
        raw_url = raw_url[7:]
    return raw_url


options_sum = args()
t_url = t_url_strip(options_sum.targ_url)
target_links = []


def req(url):
    try:
        response = requests.get("http://" + url)  # По умолчанию работает редиррект на HTTPS и он берет оба варианта
    except requests.exceptions.RequestException:
        print("\033[0;31m[-] \033[0;33mNo response from host")
        sys.exit(1)  # Завершаем выполнение скрипта, если нет ответа от сервера

    resp = (str(response.content)).replace(' ', '').replace("\\\'",
                                                            "\"")  # Удаляем пробелы, заменяем одинарные кавычки с
    # комментированием на двойные, чтобы не пропускались результаты
    # print(resp)  # Тестируем вывод
    return re.findall("(?:src=\"|href=\")(.*?)\"", resp)


# print(req(t_url)) # Тестируем массив
def make_list(input_value):
    target_links.append(input_value)
    print(input_value)


def crawl(input_url):
    print("Making output... \r\n")
    href_links = req(input_url)
    for line in href_links:
        if "#" in line and len(line) == 1:  # Режем ссылки на себя не трогая другие со знаком "#"
            line = line.split("#")[0]
        if options_sum.internal:  # Собираем все ссылки
            if input_url in line and line not in target_links:
                make_list(line)
        elif options_sum.external:
            if len(line) > 1 and '/' in line[0] and '/' in line[1] and line not in target_links:
                line = "http:" + line  # Добавляем протокол для внешних ссылок без него
                make_list(line)
            if len(line) > 1 and line not in target_links and input_url not in line and '/' not in line[0]:
                make_list(line)
        elif options_sum.relative:
            if len(line) > 1 and '/' in line[0] and '/' not in line[1] and line not in target_links:
                line = input_url + line  # Добавляем имя сайта для относительных ссылок
                make_list(line)
        else:
            if len(line) > 1 and line not in target_links:
                if '/' in line[0] and '/' not in line[1]:
                    line = input_url + line  # Добавляем имя сайта для относительных ссылок
                    make_list(line)
                elif '/' in line[0] and '/' in line[1]:
                    line = "http:" + line  # Добавляем протокол для внешних ссылок без него
                    make_list(line)
                else:
                    make_list(line)


crawl(t_url)
