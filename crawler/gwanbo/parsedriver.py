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
import re
import json

from bs4 import BeautifulSoup
from typing import *


class GwanboDict:

    def normalize(self, text):
        return str(text.strip('() ').replace('<', '(').replace('>', ')'))

    def __init__(self, category, created_at: str, publish_id: str, toc_id: str, sequence: str, author: str,
                 title: str):
        self.id = toc_id.replace('0000000000000000', '')
        self.publish = {
            'id': publish_id.replace('0000000000000000', ''),
            'title': self.normalize(title),
            'created_at': self.normalize(created_at),
            'sequence': sequence,
            'author': self.normalize(author)
        }
        self.category = {
            'name': category['name'].replace('0000000000000000', ''),
            'id': category['id'].replace('0000000000000000', '')
        }

    def __str__(self):
        return json.dumps(vars(self), ensure_ascii=False)


class ParseDriver:
    def __init__(self):
        self.agent = 'Gwanbo'
        self.categories = {
            '헌법': {
                'id': '1316064941384000', 'regex': r'헌법제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '법률': {
                'id': '1316064739911000', 'regex': r'(법률)? ?제?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '조약': {
                'id': '1316064759392000', 'regex': r'(?P<AUTHOR>.*)조약 ?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '대통령령': {
                'id': '1316064763503000', 'regex': r'(대통령)?령? ?제?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '총리령': {
                'id': '1316064767682000', 'regex': r'총리(령|훈령)? ?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '부령': {
                'id': '1316064775344000',
                'regex': [
                    r'(?P<AUTHOR>.*)부령? ?제?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<AUTHOR>.*)령 ?제 ?(?P<SEQUENCE>[\d-]+)호(?P<TITLE>.*)',
                    r'법률제?(?P<SEQUENCE>[\d]+)호(?P<TITLE>.*)'
                ]
            },
            '훈령': {
                'id': '1510711052397000',
                'regex': r'(?P<AUTHOR>.*)(훈령)? ?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '고시': {
                'id': '1316064812423000',
                'regex': [
                    r'(?P<AUTHOR>.*)(고시|공고)제?제? ?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<AUTHOR>.*)(?P<TITLE>.*)'
                ]
            },
            '공고': {
                'id': '1316064941384000',
                'regex': [
                    r'(?P<AUTHOR>.*)?(고시|공고|고고)제?제? ?(?P<SEQUENCE>[농|\W\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<AUTHOR>.*)?제(?P<SEQUENCE>[농|\W\d-]+)호?(?P<TITLE>.*)'
                ]
            },
            '국회': {
                'id': '1316064771554000',
                'regex': r'(?P<AUTHOR>.*)(규칙|공고)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '법원': {
                'id': '1316064780807000', 'regex': [
                    r'(?P<AUTHOR>.*)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<TITLE>.*)(?P<AUTHOR>[가-힣]+)'
                ]
            },
            '헌법재판소': {
                'id': '1316064801736000',
                'regex': r'(헌법재판소)?(규칙|공시|공고|고시|공)? ?제?제?(?P<SEQUENCE>[\d-]+)?호?(?P<TITLE>.*)'
            },
            '선거관리위원회': {
                'id': '1316644783234000',
                'regex': [
                    r'중앙선거관리위원회(규칙|공고|고시)? ?제?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'중앙선거관리위원회(?P<AUTHOR>[가-힣]+)(규칙|공고)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<AUTHOR>.*)선거관리위(윈|원)회(규칙|공고|고시)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)',
                    r'(?P<AUTHOR>.*)(공고|고시)제?제?(?P<SEQUENCE>[\d-]+)호(?P<TITLE>.*)'
                ]
            },
            '감사원': {
                'id': '1316064936481000', 'regex': r'감사원(규칙|공고)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '국가인권위원회': {
                'id': '1321519597927000',
                'regex': r'국가인권위원회(규칙|공고)제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '지방자치단체': {
                'id': '1316064818185000',
                'regex': r'(?P<AUTHOR>.*)?(공고|고시)? ?제?(?P<SEQUENCE>[\d-]+)호?(?P<TITLE>.*)'
            },
            '인사': {
                'id': '1316064854672000', 'regex': [
                    r'(?P<TITLE>.*)(?P<AUTHOR>[가-힣]+)',
                    r'(?P<TITLE>.*)'
                ]
            },
            '상훈': {
                'id': '1327535627196000', 'regex': [
                    r'(?P<TITLE>.*)\((?P<AUTHOR>.*)\)',
                    r'(?P<TITLE>서훈)(?P<AUTHOR>.*)'
                ]
            },
            '기타': {
                'id': '1316064859031000',
                'regex': [
                    r'(?P<TITLE>.*)(?P<AUTHOR>[가-힣]+)',
                    r'(?P<TITLE>.*)'
                ]
            },
            '대통령지시사항': {
                'id': '1615189864687000', 'regex': [
                    r'대통령지시사항(?P<TITLE>.*)',
                    r'지시사항(?P<TITLE>.*)',
                    r'(?P<TITLE>.*)'
                ]
            }
        }

    def parse_gwanbo_title(self, title: str, category: str) -> Dict[str, str]:
        regex = re.compile(
            r"javascript:fncViewToc\('(?P<PUBLISH_ID>[\d]*)', '(?P<TOC_ID>[\d]*)', '(?P<FULL_TITLE>.*)'\)"
        )
        item = regex.search(title)

        target_regex = self.categories[category]['regex']
        item_details = None
        if type(target_regex) is list:
            for reg in target_regex:
                item_details = re.compile(reg).search(item.group('FULL_TITLE'))
                if item_details is not None:
                    break
        else:
            item_details = re.compile(target_regex).search(item.group('FULL_TITLE'))

        if item_details is None:
            print(title)
            print(item['FULL_TITLE'])

        item_publish_id = item.group('PUBLISH_ID')
        item_toc_id = item.group('TOC_ID')

        item_title = item_details.group('TITLE')

        # print(json.dumps(item_details.groupdict(), ensure_ascii=False, indent=4))
        try:
            item_sequence = item_details.group('SEQUENCE')
        except IndexError as e:
            item_sequence = ''
            # print(e, 'SEQUENCE', item_title)
        try:
            item_author = item_details.group('AUTHOR')
        except IndexError as e:
            item_author = ''
            # print(e, 'AUTHOR', item_title)

        return {
            'publish_id': item_publish_id,
            'toc_id': item_toc_id,
            'sequence': item_sequence,
            'author': item_author,
            'title': item_title
        }

    def get_list_by_date(self, date: str) -> List[GwanboDict]:
        print('=====', date, '=====')

        uri = 'https://gwanbo.mois.go.kr/user/ebook/ebookDetail.do'
        header = {

        }
        request_body = {
            'ebook_date': date,
            'ebook_gubun': 'GZT001'
        }

        response = requests.post(
            uri,
            headers=header,
            params=request_body
        )

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        gwanbo_list = []
        current_category = ''
        for item in soup.select('.sb3_plt40 > *'):
            if item.name == 'p':
                current_category = item.find('strong').text
                if '훈령' in current_category:
                    current_category = '훈령'
            elif item.name == 'ul':
                href = item.find('a')['href']

                gwanbo = self.parse_gwanbo_title(href, current_category)
                gwanbo_list.append(
                    GwanboDict(
                        {'name': current_category, 'id': self.categories[current_category]['id']},
                        date, gwanbo['publish_id'], gwanbo['toc_id'],
                        gwanbo['sequence'], gwanbo['author'], gwanbo['title']
                    )
                )

        return gwanbo_list

    def download_single_gwanbo(self, gwanbo: GwanboDict, destination: str) -> bool:
        uri = 'https://gwanbo.mois.go.kr/ezpdfwebviewer/viewer.jsp' \
              f'?contentId=0000000000000000{gwanbo.publish["id"]}:0000000000000000{gwanbo.id}:N:&reqType=docData'
        response = requests.get(uri)

        print(f'download ==> {gwanbo.publish["created_at"]}/{gwanbo.category["name"]}/{gwanbo.publish["title"]}')
        try:
            if not (os.path.isdir(destination)):
                os.makedirs(destination)
            file = os.path.join(destination, f'{gwanbo.id}.pdf')
            open(file, 'wb').write(response.content)
        except IOError as e:
            print(e)
            return False

        return True

    def download_multiple_gwanbo(self, gwanbo: List[GwanboDict], destination: str) -> bool:
        for one in gwanbo:
            if not self.download_single_gwanbo(one, destination):
                return False

        return True
