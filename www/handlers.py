#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'''
Url Handlers
'''
import os
from random import shuffle
from copy import deepcopy
from aiohttp.web_request import FileField
from logger import logger, login_logger
import re, time, json, hashlib, base64, asyncio
import markdown2

from apis import APIValueError, APIError, APIResourceNotFoundError, APIPermissionError, Page
from coreweb import get, post

from aiohttp import web
from config import configs, usernames
from common import toDict, DataObject
from utils import get_cdn_url, read_json_file

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA256 = re.compile(r'^[0-9a-f]{64}$')
COOKIE_NAME = configs.cookie.name
_COOKIE_KEY = configs.cookie.secret
YAYA_BASE_PATH = "/yaya-huiben" #configs.books.yaya_base_path
XMLY_BASE_PATH = "/xmly-huiben" #configs.books.xmly_base_path

'''
================== function ====================
'''


def find_user(hashname):
    for user in usernames:
        if hashname == user.hashname:
            return user
    return None


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    '''
    Generate cookie str by user
    :param user:
    :param max_age:
    :return:
    '''

    expires = str(int(time.time() + max_age))
    s = '{}-{}-{}'.format(user.hashname, expires, _COOKIE_KEY)
    L = [user.hashname, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid
    :param cookie_str:
    :return:
    '''

    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        if uid:
            user = find_user(uid)
        if user is None:
            return None
        return user
    except Exception as e:
        logger.exception(e)
        return None


def text2html(text):
    lines = map(lambda s: '<p>{}</p>'.format(s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def get_ip(request):
    host = request.headers.get('X-FORWARDED-FOR', None)
    if host is not None:
        logger.info("Get remote_ip from header, host: " + host)
        return host
    peername = request.transport.get_extra_info('peername')
    logger.info(peername)
    if peername is not None:
        host, port, *_ = peername
        return host
    else:
        return None


'''
====================== end function ====================
'''

'''
===================== client page =======================
'''


@get('/test')
def test(request):
    return web.Response(body=b'<h1>Awesome Python3 Web</h1>', content_type='text/html')


@get('/signin')
def signin(request):
    if request.__user__:  # user has login, redirect /
        r = web.HTTPFound('/')
        return r
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logger.info('User signed out.')
    return r


@get('/')
def index(*, page='1', age=None, labelid=None, random=None):
    page_index = get_page_index(page)
    books = DataObject.get_yaya_books(age=age, labelid=labelid)
    if random == 'true':
        books = deepcopy(books)
        shuffle(books)
    num = len(books)
    p = Page(num, page_index)
    return {
        'page': p,
        'ages': DataObject.ages,
        'labels': DataObject.get_labels(),
        'current_age': age,
        'current_label': labelid,
        'current_random': random,
        'books': () if num == 0 else books[p.offset: p.offset + p.limit],
        '__template__': 'index.html'
    }


@get('/xmly')
def xmly_index(*, page='1', albumid=None, random=None):
    page_index = get_page_index(page)
    books = DataObject.get_xmly_books(albumid=albumid)
    if random == 'true':
        books = deepcopy(books)
        shuffle(books)
    albums = DataObject.get_xmly_albums()
    num = len(books)
    p = Page(num, page_index)
    return {
        'page': p,
        'albums': albums,
        'books': () if num == 0 else books[p.offset: p.offset + p.limit],
        'current_album': albumid,
        'current_random': random,
        '__template__': 'index_xmly.html'
    }


@get('/yaya-book')
def yaya_book(*, id=None):
    book = DataObject.get_yaya_books(id=id)
    book_data = None
    if book:
        book = book[0]
        book_json_name = f"/{YAYA_BASE_PATH}/{book['id']}.{book['name']}/{book['id']}.resourceDetail.json"
        book_data = read_json_file(book_json_name)['data']

    res_data = {
        'announcer': '白宇航',
        'id': 2269,
        'name': '咪子的家',
        'ageDesc': '4-6岁',
        'cover': 'http://cover.yayagushi.com/e29ae422522840f58294f06b5b9572d7_%s.png',
        'desc': '小女孩有一只小猫“咪子”，一天它突然消失了。小女孩体验了失去并寻找咪子的失望和希望，也收获了新生命的惊奇和感动。\n\n猫咪带给了女孩生命的启示，关于信任、母性之爱。故事质朴温暖、情感真挚。',
        'estimatedChapter': 16,
        'totalChapter': 16,
        'labelList': ['爱与情感', '生命', '温暖', '亲情', '友情', '动物']
    }
    if book_data:
        res_data['announcer'] = book_data['announcer']['nickName']
        res_data['id'] = book_data['resource']['id']
        res_data['name'] = book_data['resource']['name']
        res_data['ageDesc'] = book_data['resource']['ageDesc']
        res_data['cover'] = book_data['resource']['cover'].replace('http://', '//').replace('.png', '_%s.png')
        res_data['desc'] = book_data['resource']['desc'].replace('\n', '<br />')
        res_data['estimatedChapter'] = book_data['resource']['estimatedChapter']
        res_data['totalChapter'] = book_data['resource']['totalChapter']
        res_data['labelList'] = book_data['resource']['labelList']
        res_data['priceType'] = book_data['resource']['priceType']

    return {
        'book': toDict(res_data),
        '__template__': 'yaya_book.html'
    }


@get('/xmly-book')
def xmly_book(*, id=None):
    book = DataObject.get_xmly_books(id=id)
    book_data = None
    albums = None
    if book:
        book = book[0]
        book['audio'] = get_cdn_url(f"/{XMLY_BASE_PATH}/{book['recordId']}.{book['recordTitle'].replace('|', '')}/{book['recordTitle'].replace('|', '')}.m4a")
        book_json_name = f"/{XMLY_BASE_PATH}/{book['recordId']}.{book['recordTitle'].replace('|', '')}/{book['recordId']}.{book['recordTitle']}.json"
        book_screen = read_json_file(book_json_name)
        book['count'] = book_screen['screenCnt']

        album_id = book['albumId']
        album = DataObject.get_xmly_albums(album_id)
        if album:
            album = album[0]

    return {
        'book': toDict(book),
        'album': toDict(album),
        '__template__': 'xmly_book.html'
    }


'''
====================== end client page =====================
'''

'''
==================== backend api ====================
'''


@post('/api/authenticate')
def authenticate(*, username, remember):
    if not username:
        raise APIValueError('username', '无效姓名！')
    user = find_user(username)
    if not user:
        raise APIValueError('username', '无效姓名！')

    #record login
    login_logger.info(user.username)

    # authenticate ok, set cookie
    r = web.Response()
    if remember:
        max_age = configs.cookie.max_age_long
    else:
        max_age = configs.cookie.max_age
    r.set_cookie(COOKIE_NAME, user2cookie(user, max_age), max_age=max_age, httponly=True)
    #user.username = ''
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


'''-----------books------------'''


@get('/api/yaya-book/{id}')
async def api_yaya_book_detail(*, id):
    book = DataObject.get_yaya_books(id=id)
    book_list = None
    if book:
        book = book[0]
        book_json_name = f"/{YAYA_BASE_PATH}/{book['id']}.{book['name'].replace('|', '')}/{book['id']}.chapterList.json"
        book_list = read_json_file(book_json_name)

    if book_list:
        for item in book_list:
            item['cover'] = item['cover'].replace('http://', '//')
            item['audio_url'] = get_cdn_url(f"/{YAYA_BASE_PATH}/{book['id']}.{book['name'].replace('|', '')}/audio/{item['name']}.mp3")
            item['cover_url'] = get_cdn_url(f"/{YAYA_BASE_PATH}/{book['id']}.{book['name'].replace('|', '')}/img/{item['name']}.png")
            text_json_name = f"/{YAYA_BASE_PATH}/{book['id']}.{book['name'].replace('|', '')}/json/{item['id']}.{item['name']}.json"
            item['content'] = read_json_file(text_json_name)['data']['chapter']['content']
    return dict(book_list=book_list)


@get('/api/yaya-books')
async def api_yaya_books(*, page='1'):
    page_index = get_page_index(page)
    books = DataObject.get_yaya_books()
    num = len(books)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, books=())
    books = books[p.offset: p.limit]
    return dict(page=p, books=books)


@get('/api/xmly-book/{id}')
async def api_xmly_book_detail(*, id):
    book = DataObject.get_xmly_books(id=id)
    book_screen = None
    if book:
        book = book[0]
        book_json_name = f"/{XMLY_BASE_PATH}/{book['recordId']}.{book['recordTitle'].replace('|', '')}/{book['recordId']}.{book['recordTitle'].replace('|', '')}.json"
        book_screen = read_json_file(book_json_name)['screens']

    if book_screen:
        for item in book_screen:
            item['cover_url'] = get_cdn_url(f"/{XMLY_BASE_PATH}/{book['recordId']}.{book['recordTitle'].replace('|', '')}/imgs/{item['index']}.jpg")

    return dict(book_screen=book_screen)


@get('/api/xmly-books')
async def api_xmly_books(*, page='1'):
    page_index = get_page_index(page)
    books = DataObject.get_xmly_books()
    num = len(books)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, books=())
    books = books[p.offset: p.limit]
    return dict(page=p, books=books)
