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
    dates = [date.today() - timedelta(days=i) for i in range(0, days + 1)]
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
        data[d].append(name)
    return data


def main():
    filename = 'download.out'
    db_filename = 'data.db'
    days = 7

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
    data = [
        dict(value=tag, date=d)
        for d, tags in raw_data.items()
        for tag in tags
    ]
    exist.post('/attributes/custom/append/', json=data)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    main()
