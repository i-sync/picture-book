#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import logging
from logger import logger, login_logger
import os.path

import asyncio
import json
import time
import os
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from coreweb import add_routes, add_static
from handlers import cookie2user, COOKIE_NAME
from config import configs
from utils import verify_sign


def init_jinja2(app, **kwargs):
    logger.info('init jinja2...')
    options = dict(
        autoescape=kwargs.get('autoescape', True),
        block_start_string=kwargs.get('block_start_string', '{%'),
        block_end_string=kwargs.get('blcok_end_string', '%}'),
        variable_start_string=kwargs.get('variable_start_string', '{{'),
        variable_end_string=kwargs.get('variable_end_string', '}}'),
        auto_reload=kwargs.get('auto_reload', True)
    )
    path = kwargs.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logger.info('set jinja2 template path: {}'.format(path))
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kwargs.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def logger_factory(app, handler):
    async def inner_logger(request):
        if request.path != '/api/logs':  # skip /api/logs
            logger.info('Request: {} {}'.format(request.method, request.path))
        return await handler(request)

    return inner_logger


async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logger.info('request json: {}'.format(str(request.__data__)))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logger.info('request form: {}'.format(str(request.__data__)))
        return await handler(request)

    return parse_data


async def auth_factory(app, handler):
    async def auth(request):
        # logger.info('check user: {} {}'.format(request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                login_logger.info(f"set current user: [{user.username}] {request.path_qs}")
                request.__user__ = user
        # handle cdn static request
        if request.path.startswith(('/yaya-huiben/', '/xmly-huiben/')) \
                and 'sign' in request.query \
                and verify_sign(request.path, request.query['sign']):
            return await handler(request)
        if not request.path.startswith('/static') \
                and not request.path.startswith('/signin') \
                and not request.path.startswith('/api/authenticate') \
                and request.__user__ is None:
            return web.HTTPFound('/signin')
        return await handler(request)

    return auth


async def response_factory(app, handler):
    async def response(request):
        # logger.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            res = web.Response(body=r)
            res.content_type = 'application/octet-stream'
            return res
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            res = web.Response(body=r.encode('utf-8'))
            res.content_type = 'application/json; charset=utf-8'
            return res
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                res = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                res.content_type = 'application/json;charset=utf-8'
                return res
            else:
                r['__user__'] = request.__user__
                res = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                res.content_type = 'text/html;charset=utf-8'
                return res
        if isinstance(r, int) and 100 <= r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and 100 <= t < 600:
                return web.Response(t, str(m))
        # default:
        res = web.Response(body=str(r).encode('utf-8'))
        res.content_type = 'text/plain;charset=utf-8'
        return res

    return response


def datetime_filter(t):
    date_time = datetime.fromtimestamp(t)
    str_date = date_time.strftime("%Y-%m-%d %X")
    delta = int(time.time() - t)
    if delta < 60:
        return u'<span title="{}">1分钟前</span>'.format(str_date)
    if delta < 3600:
        return u'<span title="{}">{}分钟前</span>'.format(str_date, delta // 60)
    if delta < 86400:
        return u'<span title="{}">{}小时前</span>'.format(str_date, delta // 3600)
    if delta < 604800:
        return u'<span title="{}">{}天前</span>'.format(str_date, delta // 86400)
    # dt = datetime.fromtimestamp(t)
    return u'<span title="{}">{}</span>'.format(str_date, date_time.strftime("%Y-%m-%d"))


def ensure_http(url):
    if url.startswith("http") or url.startswith("https"):
        return url
    else:
        return "http://" + url


# def index(request):
# return web.Response(body=b'<h1>Awesome Python3 Web</h1>', content_type='text/html')

async def init(loop):
    # logger.info(configs.database)
    # await orm.create_pool(loop=loop, **configs.database)
    app = web.Application(client_max_size=1024**2*5, loop=loop, middlewares=[
        logger_factory, data_factory, auth_factory, response_factory
    ])
    init_jinja2(app, filters=dict(datetime=datetime_filter, ensure_http=ensure_http))
    add_routes(app, 'handlers')
    add_static(app)
    # app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 8080)
    logger.info('Server started at http://127.0.0.1:8080...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
