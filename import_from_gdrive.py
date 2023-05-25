#!/usr/bin/env python
import logging
import shutil
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from zipfile import ZipFile

import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import exist
import settings
from util import chunks


def download_gdrive_file(service, file_id, filename):
    content = service.files().get_media(fileId=file_id).execute()
    with open(filename, 'wb') as f:
        f.write(content)


def unzip(filename, db_filename):
    with ZipFile(filename) as zipfile:
        with zipfile.open('databases/Rewire.db') as zf, open(db_filename, 'wb') as f:
            shutil.copyfileobj(zf, f)


def select_data(connection, dates):
    dates = "', '".join([d.strftime('%Y%m%d') for d in dates])
    # noinspection SqlNoDataSourceInspection
    sql = """
        SELECT `date`, `description`, `type`
        FROM checkins
        JOIN habits ON habits._id = habit_id
        WHERE `date` IN ('{}')
          AND `type` IN (1, 2)
          AND `description` != ''
        ORDER BY `date`, `description`
        """.format(dates)
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        yield row


def collect_data(db_filename, days):
    connection = sqlite3.connect(db_filename)
    today = date.today()
    dates = [
        today - timedelta(days=i)
        for i in range(0, days + 1)
    ]
    raw_data = select_data(connection, dates)
    data = defaultdict(list)
    for d, name, t in raw_data:
        if name.startswith('!'):  # reverse logic (bad habits)
            name = name[1:]
            if t == 2:  # success
                continue
        else:
            if t == 1:  # fail
                continue
        d = datetime.strptime(d, '%Y%m%d').strftime('%Y-%m-%d')
        name = name.replace(' ', '_')
        data[d].append(name)
    return data


def acquire(tags):
    tags = list(tags)
    tags = sorted(tags)
    print(f'acquire {len(tags)} tags: {tags}')
    failed = []
    for chunk in chunks(tags, exist.LIMIT_MAXIMUM_OBJECTS_PER_REQUEST):
        result = exist.post('/attributes/acquire/', json=[
            dict(name=tag)
            for tag in chunk
        ]).json()
        failed.extend(result.get('failed') or [])
    if not failed:
        return
    create_tags = []
    for element in failed:
        if element['error_code'] == 'not_found':
            create_tags.append(element['name'])
    if not create_tags:
        return
    print(f'creating {len(create_tags)} tags: {create_tags}')
    exist.post('/attributes/create/', json=[
        dict(
            name=tag,
            label=tag.replace('_', ' '),
            group='custom',
            manual=True,
            value_type=7,  # boolean (the only option available for custom attributes)
        )
        for tag in create_tags
    ])


def main(days: int):
    filename = 'download.out'
    db_filename = 'data.db'

    if settings.file_url:
        response = requests.get(settings.file_url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        assert settings.file_id
        credentials = Credentials.from_service_account_file('credentials.json')
        service = build('drive', 'v3', credentials=credentials)
        download_gdrive_file(service, settings.file_id, filename)
    unzip(filename, db_filename)
    raw_data = collect_data(db_filename, days)
    unique_tags = set()
    data = []
    for d, tags in raw_data.items():
        for tag in tags:
            tag = tag.strip().strip('-')
            unique_tags.add(tag)
            data.append(dict(name=tag, date=d, value=1))
    acquire(unique_tags)
    for chunk in chunks(data, exist.LIMIT_MAXIMUM_OBJECTS_PER_REQUEST):  # there's a limit
        exist.post('/attributes/update/', json=chunk)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--days', help='How many days to process', default=10, type=int)
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    assert args.days >= 1, 'Should be at least 1 day to process'
    main(args.days)
