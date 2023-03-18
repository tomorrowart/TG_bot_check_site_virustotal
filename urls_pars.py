import re

async def extract_links(text):
    # регулярное выражение для поиска ссылок
    print(text)
    url_regex = r"(https?://\S+)"
    # используем функцию findall модуля re для извлечения ссылок из текста
    #text = text.replace(',', '').replace(':', '').replace(';', '').replace('"', '')
    urls = re.findall(url_regex, text)
    return urls