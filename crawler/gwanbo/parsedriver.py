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
from bs4 import BeautifulSoup
from typing import *


class GwanboDict:
    def __init__(self, category: str, date: str, content_id: str, toc_id: str, name: str):
        self.category = category
        self.date = date
        self.content_id = content_id
        self.toc_id = toc_id
        self.name = name.strip().replace('<', '(').replace('>', ')')


class ParseDriver:
    def __init__(self):
        self.agent = 'Gwanbo'
        self.categories = {
            '헌법': '00000000000000001316064941384000',
            '법률': '00000000000000001316064739911000',
            '조약': '00000000000000001316064759392000',
            '대통령령': '00000000000000001316064763503000',
            '총리령': '00000000000000001316064767682000',
            '부령': '00000000000000001316064775344000',
            '훈령': '00000000000000001510711052397000',
            '고시': '00000000000000001316064812423000',
            '공고': '00000000000000001316064941384000',
            '국회': '00000000000000001316064771554000',
            '법원': '00000000000000001316064780807000',
            '헌법재판소': '00000000000000001316064801736000',
            '선거관리위원회': '00000000000000001316644783234000',
            '감사원': '00000000000000001316064936481000',
            '국가인권위원회': '00000000000000001321519597927000',
            '지방자치단체': '00000000000000001316064818185000',
            '인사': '00000000000000001316064854672000',
            '상훈': '00000000000000001327535627196000',
            '기타': '00000000000000001316064859031000',
            '전체': '00000000000000001615189864687000'
        }

    def getListByDate(self, date: str) -> List[GwanboDict]:
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
            else:
                href = item.find('a')['href']
                regex = re.compile(r"javascript:fncViewToc\('([\d]*)', '([\d]*)', '(.*)'\)")
                items = regex.search(href)
                gwanbo_list.append(
                    GwanboDict(current_category, date, items[1], items[2], items[3])
                )

        return gwanbo_list

    def download_single_gwanbo(self, gwanbo: GwanboDict) -> bool:
        uri = 'https://gwanbo.mois.go.kr/ezpdfwebviewer/viewer.jsp' \
              f'?contentId={gwanbo.content_id}:{gwanbo.toc_id}:N:&reqType=docData'

        response = requests.get(uri)

        try:
            directory = os.path.join('data', gwanbo.date, gwanbo.category)
            if not (os.path.isdir(directory)):
                os.makedirs(directory)
            file = os.path.join(directory, f'{gwanbo.name}.pdf')
            open(file, 'wb').write(response.content)
        except IOError as e:
            print(e)
            return False

        return True

    def download_multiple_gwanbo(self, gwanbo: List[GwanboDict]) -> bool:
        for one in gwanbo:
            if not self.download_single_gwanbo(one):
                return False

        return True
