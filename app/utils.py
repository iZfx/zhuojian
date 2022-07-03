from urllib.parse import urlparse, urljoin
from flask import request, url_for, current_app
from jinja2.filters import do_striptags
from jieba import posseg as pseg

# 使用重定向的方式返回上一个页面
from werkzeug.utils import redirect


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def get_search_part(content, search_str, left_offset=30, part_len=260):
    """
    根据搜索内容截取文章正文中相关的内容
    :param content: 文章正文
    :param search_str: 搜索内容
    :param left_offset: 左偏移量 default = 30
    :param part_len: 截取的内容总长 default = 260
    :return: 截取后的内容
    """
    no_tag_content = do_striptags(content)
    search_position = no_tag_content.lower().find(search_str.lower())
    start_position = max(0, search_position - left_offset)
    search_part = no_tag_content[start_position: start_position + part_len]
    if search_position - left_offset > 0:
        search_part = f'....{search_part}'
    if search_position + part_len < len(no_tag_content):
        search_part = f'{search_part}....'
    search_part = search_part.replace(search_str, f'<font color="#ff3366">{search_str}</font>')
    return search_part


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# 分词过滤，用jieba模块进行分词并去掉无用词
def tokenization(content):
    '''
    {标点符号、连词、助词、副词、介词、时语素、‘的’、数词、方位词、代词}
    {'x', 'c', 'u', 'd', 'p', 'tg', 'uj', 'm', 'f', 'r'}
    去除文章中特定词性的词
    :content str
    :return list[str]
    '''
    stop_flags = {'x', 'c', 'u', 'd', 'p', 'tg', 'uj', 'm', 'f', 'r'}
    stop_words = {'nbsp', '\u3000', '\xa0'}
    words = pseg.cut(content)
    return [word for word, flag in words if flag not in stop_flags and word not in stop_words]
