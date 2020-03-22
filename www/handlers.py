#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'''
Url Handlers
'''
import os

from aiohttp.web_request import FileField
from logger import logger
import re, time, json, hashlib, base64, asyncio
import markdown2

from apis import APIValueError, APIError, APIResourceNotFoundError, APIPermissionError, Page
from coreweb import get, post

from models import Album, Story, PlayIndex, PlayStatus, StatisticView, next_id
from orm import select, execute
from aiohttp import web
from config import configs, usernames
from common import toDict, DataObject

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA256 = re.compile(r'^[0-9a-f]{64}$')
COOKIE_NAME = configs.cookie.name
_COOKIE_KEY = configs.cookie.secret
BOOK_BASE_PATH = configs.books.base_path

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
def index(*, page='1', age=None, labelid=None):
    page_index = get_page_index(page)
    books = DataObject.get_books(age = age, labelid = labelid)
    num = len(books)
    p = Page(num, page_index)
    return {
        'page': p,
        'ages': DataObject.ages,
        'labels': DataObject.get_labels(),
        'current_age': age,
        'current_label': labelid,
        'books': () if num == 0 else books[p.offset: p.offset + p.limit],
        '__template__': 'index.html'
    }

@get('/book')
def book(*, id=None):
    book = DataObject.get_books(id=id)
    book_data = None
    if book:
        book = book[0]
        book_json_name = f"{BOOK_BASE_PATH}/{book['id']}.{book['name'].replace('|','')}/{book['id']}.resourceDetail.json"
        if os.path.exists(book_json_name):
            with open(book_json_name, 'r', encoding='utf-8') as f:
                book_data = json.load(f)['data']

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
        res_data['cover'] = book_data['resource']['cover'].replace('.png', '_%s.png')
        res_data['desc'] = book_data['resource']['desc'].replace('\n', '<br />')
        res_data['estimatedChapter'] = book_data['resource']['estimatedChapter']
        res_data['totalChapter'] = book_data['resource']['totalChapter']
        res_data['labelList'] = book_data['resource']['labelList']


    return {
        'book': toDict(res_data),
        '__template__': 'book.html'
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
    # authenticate ok, set cookie
    r = web.Response()
    if remember:
        max_age = configs.cookie.max_age_long
    else:
        max_age = configs.cookie.max_age
    r.set_cookie(COOKIE_NAME, user2cookie(user, max_age), max_age=max_age, httponly=True)
    user.name = ''
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


'''-----------books------------'''


@get('/api/book/{id}')
async def api_get_book_list(*, id):
    book = DataObject.get_books(id=id)
    book_list = None
    if book:
        book = book[0]
        book_json_name = f"{BOOK_BASE_PATH}/{book['id']}.{book['name'].replace('|','')}/{book['id']}.chapterList.json"
        if os.path.exists(book_json_name):
            with open(book_json_name, 'r', encoding='utf-8') as f:
                book_list = json.load(f)

    if book_list:
        for item in book_list:
            item['audio_url'] = f"/static/books/{book['id']}.{book['name'].replace('|','')}/audio/{item['name']}.mp3"
            item['cover_url'] = f"/static/books/{book['id']}.{book['name'].replace('|','')}/img/{item['name']}.webp"
            text_json_name = f"{BOOK_BASE_PATH}/{book['id']}.{book['name'].replace('|','')}/json/{item['id']}.{item['name']}.json"
            if os.path.exists(text_json_name):
                with open(text_json_name, 'r', encoding='utf-8') as f:
                    item['content'] = json.load(f)['data']['chapter']['content']
    return dict(book_list=book_list)

@get('/api/books')
async def api_get_books(*, page='1'):
    page_index = get_page_index(page)
    books = get_books()
    num = len(books)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, books=())
    books = books[p.offset: p.limit]
    return dict(page=p, books=books)


'''-----------play_status-----------'''
@post('/api/play_status/{id}/delete')
async def api_delete_play_status(request, *, id):
    logger.info('delete play_status id: {}'.format(id))
    check_admin(request)
    play_status = await PlayStatus.find(id)
    if play_status:
        await play_status.remove()
        return play_status
    raise APIValueError('id', 'id can not find...')

'''-----------statistics------------'''


@get('/api/statistics')
async def api_statistics(request, *, page='1', device_id=None, album_id=None, token=None, column_name=None, direction=None):
    page_index = get_page_index(page)
    num = 0
    where = []
    args = []

    sql = '''
    SELECT count(play_status.id) as _num_
    from play_status
    inner join story on story.token = play_status.token
    '''

    if device_id and device_id != 'None':
        where.append(' play_status.device_id=?')
        args.append(device_id)
    if album_id and album_id != 'None':
        where.append('AND story.album_id=?' if len(where) else ' story.album_id=?')
        args.append(album_id)
    if token and token != 'None':
        where.append('AND play_status.token=?' if len(where) else ' play_status.token=?')
        args.append(token)

    if len(where):
        rs = await select(sql + 'where' + ' '.join(where), args, 1)
        if len(rs):
            num = rs[0]['_num_']
    else:
        num = await PlayStatus.find_number('count(id)')

    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, statistics=())

    sql = '''
    SELECT play_status.id, play_status.device_id, album.id as album_id, album.album_name, play_status.token, story.id as story_id, story.story_name, story.order_in_album, play_status.offset, play_status.finished, play_status.finished_times, play_status.updated_at, case when play_status.token = play_index.token then True else False end as current_token
    from play_status
    left join story on story.token = play_status.token
    left join album on album.id = story.album_id
    left join play_index on play_status.device_id = play_index.device_id and story.album_id = play_index.album_id 
    '''
    if column_name and column_name != 'None':
        order = f' order by {column_name} {"desc" if direction and direction=="descending" else "asc"} limit ?, ?;'
    else:
        order = ' order by device_id, album_id, order_in_album asc limit ?, ?;'
    args.extend([p.offset, p.limit])
    rs = await select(sql + 'where' + ' '.join(where) + order if len(where) else sql + order, args)
    statistics = [StatisticView(**r) for r in rs]
    return dict(page=p, statistics=statistics)


'''-------------data imports-------------'''


@get('/api/imports')
async def api_imports(request, *, page='1'):
    check_admin(request)
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/import-data'
    data_file_names = [x for x in os.listdir(file_path) if x.endswith(".json")]
    page_index = get_page_index(page)
    num = len(data_file_names)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, filenames=())

    res = []
    for file_name in data_file_names:
        create_time = os.path.getctime(f'{file_path}/{file_name}')
        modify_time = os.path.getmtime(f'{file_path}/{file_name}')
        file_size = os.path.getsize(f'{file_path}/{file_name}')
        res.append({'file_name': file_name, 'create_time': create_time, 'modify_time': modify_time, 'file_size': file_size})
    return dict(page=p, filenames=res)

@post('/api/import/read')
async def api_get_file(request, *, file_name):
    check_admin(request)
    # read json
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/import-data/{file_name}'
    if not os.path.exists(file_path):
        raise APIResourceNotFoundError(f'{file_path} not found.')

    res = ''
    with open(file_path, 'r', encoding='utf-8') as f:
        # json_data = json.load(f)
        res = f.read()
    return res

@post('/api/import/json')
async def api_import_data(request, *, file_name):
    check_admin(request)
    # read json
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/import-data/{file_name}'
    if not os.path.exists(file_path):
        raise APIResourceNotFoundError(f'{file_path} not found.')
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # import
    res = []
    for json_album in json_data:
        album_name = json_album['name']
        origin_name = json_album['origin_name']
        name_keys = '\n'.join(json_album['keys'])
        story_count = json_album['count']
        # check album if exists
        album = await Album.find_all(where='album_name=?', args=[album_name])
        if len(album):
            album[0].description = "SKIP, Album has been imported."
            res.append(album[0])
            continue
        album = Album(album_name=album_name, origin_name=origin_name, name_keys=name_keys, story_count=story_count,
                      is_publish=True)
        await album.save()
        res.append(album)
        index = 1
        for json_story in json_album['list']:
            story_name = json_story['name']
            token = json_story['token']
            play_url = json_story['url'].replace('http://a1.xpath.org', '')
            audio_type = 'MP3' if json_story['stream_format'] == 'mp3' else 'M4A'
            story = Story(album_id=album.id, story_name=story_name, token=token, order_in_album=index,
                          play_url=play_url, audio_type=audio_type, enable=True)

            await story.save()
            index += 1
    return json.dumps(res, ensure_ascii=False, indent=True)


'''-------------logs-------------'''
@get('/api/logs')
async def api_read_logs(request):
    check_admin(request)
    logs = read_logs()
    return dict(logs=logs)



'''-------------names-------------'''
@get('/api/names')
async def api_album_names(request):
    check_admin(request)
    albums = await Album.find_all(order_by='is_publish desc, album_name asc')
    names = [album.album_name for album in albums]
    return dict(names='\n'.join(names))

'''
==================== end backend api ====================
'''
