#!/usr/bin/env python
import logging

import requests

import settings

logger = logging.getLogger(__name__)
api_version = 2
base_url = 'https://exist.io/api/{}/'.format(api_version)

LIMIT_MAXIMUM_OBJECTS_PER_REQUEST = 35


def request(method, path, **kwargs):
    method = method.upper()
    path = path.lstrip('/')
    kwargs.setdefault('headers', {
        'Authorization': 'Bearer ' + settings.access_token,
    })
    url = base_url + path
    logger.debug('request {} {}'.format(method, url))
    response = requests.request(method, url, **kwargs)
    logger.debug('status: {}'.format(response.status_code))
    result = response.json()
    detail = result.get('detail')
    if detail:
        logger.error(f'error with detail: {detail} in request "{path}"')
    failed = result.get('failed')
    if failed:
        logger.error(f'failed: {failed} in request "{path}"')
    return response


def get(path, params=None, **kwargs):
    return request('get', path, params=params, **kwargs)


def post(path, **kwargs):
    return request('post', path, **kwargs)


def refresh_token():
    return requests.post(
        'https://exist.io/oauth2/access_token',
        {
            'grant_type': 'refresh_token',
            'refresh_token': settings.refresh_token,
            'client_id': settings.EXISTIO_CLIENT_ID,
            'client_secret': settings.EXISTIO_CLIENT_SECRET,
        },
    )
