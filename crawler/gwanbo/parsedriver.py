"""
    Copyright (c) 2021 Aaron(JIN, Taeyang).
    All rights reserved. This program and the accompanying materials
    are made available under the terms of the GNU Lesser General Public License v2.1
    which accompanies this distribution, and is available at
    https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

    Contributors:
        Aaron(JIN, Taeyang) - Create gwanbo/parsedriver
"""
import os
import requests
import json

from typing import *

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dateutil.parser import parse

import urllib


class GwanboDict:
    def __init__(self, agent: str, seq: str, ebook_no: str, publish_seq: str, publish_subject: str,
                 publish_regdate: str, organization_name: str, organization_code: str, category_name: str,
                 category_seq: str, law_name: str):
        self.seq = seq
        self.ebookNo = ebook_no
        self.publish = {
            'seq': publish_seq,
            'subject': publish_subject.strip(),
            'regdate': publish_regdate.replace('20107280', '20100728')
        }
        self.organization = {
            'name': organization_name,
            'code': organization_code
        }
        self.category = {
            'name': category_name,
            'seq': category_seq
        }

        self.lawName = law_name.strip()

        dt = parse(self.publish["regdate"])
        _cdn_prefix = f'https://cdn.dataportal.kr/data/{agent}/{dt.year}/{dt.month}/{dt.day}/'
        self.binaryFile = f'{_cdn_prefix}{self.seq}.pdf'

    def __str__(self):
        return json.dumps(vars(self), ensure_ascii=False)


class ParseDriver:
    def __init__(self):
        self.agent = 'gwanbo'

    def get_list_by_date(self, start_date: str, end_date: str) -> List[GwanboDict]:
        print(f'===== {start_date} TO {end_date} =====')

        session = requests.session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        url = 'https://gwanbo.go.kr/SearchRestApi.jsp'
        header = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        request_body = {
            'mode': 'daily',
            'index': 'gwanbo',
            'query': f'keyword_field_regdate:[{start_date}+TO+{end_date}]+AND+unstored_field_keyword:(관보)+AND+keyword_category_order:(@@ORDER_NUM)',
            'pQuery_tmp': '',
            'pageNo': '1',
            'listSize': '10000',
            'sort': ''
        }
        request_payload = ''
        for k, v in request_body.items():
            request_payload += f'{k}={urllib.parse.quote(v).replace("%2B", "+")}&'

        response = session.post(
            url,
            headers=header,
            data=request_payload
        )
        try:
            dataset = json.loads(response.text)['data']
        except Exception as e:
            return list()

        gwanbo_list = list()
        for data in dataset:
            if data['count'] > 0:
                for item in data['list']:
                    gwanbo_list.append(GwanboDict(
                        self.agent,
                        item['stored_toc_seq'], item['keyword_ebook_no'], item['search_key'].split('_')[1],
                        item['stored_field_subject'], item['keyword_field_regdate'], item['stored_organ_nm'],
                        item['stored_organ_code'], item['stored_category_name'], item['stored_category_seq'],
                        item['stored_laword_nm']
                    ))
        return gwanbo_list

    def download_single_gwanbo(self, gwanbo: GwanboDict, destination: str) -> bool:
        session = requests.session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        uri = 'https://gwanbo.go.kr/ezpdfwebviewer/viewer.jsp?optNoUi=true&optLang=ko&' \
              f'contentId={gwanbo.publish["seq"]}":{gwanbo.seq}:N:&reqType=docData&reqSubType=dn'
        response = session.get(uri)

        print(f'download ==> {gwanbo.publish["regdate"]}/{gwanbo.category["name"]}/{gwanbo.publish["subject"]}')
        try:
            if not (os.path.isdir(destination)):
                os.makedirs(destination)
            file = os.path.join(destination, f'{gwanbo.seq}.pdf')
            open(file, 'wb').write(response.content)
        except IOError as e:
            print('IOError', e)
            return False
        return True

    def download_multiple_gwanbo(self, gwanbo: List[GwanboDict], destination: str) -> bool:
        for one in gwanbo:
            if not self.download_single_gwanbo(one, destination):
                return False

        return True
