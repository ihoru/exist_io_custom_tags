#!/usr/bin/env python

import requests

import settings

api_version = 1
base_url = 'https://exist.io/api/{}/'.format(api_version)


def request(method, path, **kwargs):
    method = method.upper()
    path = path.lstrip('/')
    kwargs.setdefault('headers', {
        # 'Authorization': 'Token ' + settings.token,
        'Authorization': 'Bearer ' + settings.access_token,
    })
    url = base_url + path
    print('-' * 100)
    print(method, url)
    print(kwargs)
    response = requests.request(method, url, **kwargs)
    print(response.text)
    return response


def get(path, params=None, **kwargs):
    return request('get', path, params=params, **kwargs)


def post(path, **kwargs):
    return request('post', path, **kwargs)
