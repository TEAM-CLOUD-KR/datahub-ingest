"""
    Copyright (c) 2021 Aaron(JIN, Taeyang).
    All rights reserved. This program and the accompanying materials
    are made available under the terms of the GNU Lesser General Public License v2.1
    which accompanies this distribution, and is available at
    https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

    Contributors:
        Aaron(JIN, Taeyang) - Create Main Application
"""
import os
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.gwanbo import parsedriver as GwanboDriver
from crawler.jsonencoder import JsonEncoder
from s3client import client as S3Client

from multiprocessing import Pool
from dateutil.parser import parse

import datetime
import json


class Application:
    def __init__(self, parser):
        config = None
        config_file = 'datahub-ingest.json'
        windows_dir = os.path.join('c:\\', 'repository', '_secrets', config_file)
        linux_dir = os.path.join('/', 'home', 'datahub', '_secrets', config_file)
        mac_dir = os.path.join('/', 'Users', 'sun', 'repository', '_secrets', config_file)

        if os.path.exists(windows_dir):
            with open(windows_dir, 'r') as f:
                config = json.load(f)

        if os.path.exists(linux_dir):
            with open(linux_dir, 'r') as f:
                config = json.load(f)

        if os.path.exists(mac_dir):
            with open(mac_dir, 'r') as f:
                config = json.load(f)

        if config is None:
            print('===== CAN NOT FOUND CONFIG FILE =====')
            exit()

        self.aws_access_key_id = config['S3']['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = config['S3']['AWS_SECRET_ACCESS_KEY']

        self.parser = parser

    def download_and_upload_gwanbo_to_s3(self, gwanbo: GwanboDriver.GwanboDict):
        dt = parse(gwanbo.publish["createdAt"])
        directory = os.path.join('data', self.parser.agent, str(dt.year), str(dt.month), str(dt.day))

        try:
            self.parser.download_single_gwanbo(gwanbo, directory)

            source_file = os.path.join(directory, gwanbo.id + '.pdf')
            client = S3Client.Client(self.aws_access_key_id, self.aws_secret_access_key)
            res = client.upload_file('data-portal-cdn', source_file, source_file.replace('\\', '/'))

            os.remove(source_file)
        except Exception as e:
            print(e)

    def sync_mariadb(self, gwanbo: GwanboDriver.GwanboDict):
        session = requests.session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        url = 'https://www.dataportal.kr/core/gwanbo'
        header = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = session.post(
            url,
            headers=header,
            data=str(gwanbo).encode('utf-8')
        )

        return response.json()


if __name__ == '__main__':
    app = Application(GwanboDriver.ParseDriver())

    gwanbo_list = app.parser.get_list_by_date(datetime.datetime.today().strftime('%Y%m%d'))

    json_directory = os.path.join('data', app.parser.agent)
    if not (os.path.isdir(json_directory)):
        os.makedirs(json_directory)
    file = os.path.join(json_directory, 'data.json')

    with open(file, 'w', encoding='utf-8') as json_file:
        json.dump(gwanbo_list, fp=json_file, ensure_ascii=False, cls=JsonEncoder)

    for gwanbo_item in gwanbo_list:
        app.download_and_upload_gwanbo_to_s3(gwanbo_item)
        print(app.sync_mariadb(gwanbo_item))

    print('====================')
