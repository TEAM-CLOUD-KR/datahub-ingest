"""
    Copyright (c) 2021 Aaron(JIN, Taeyang).
    All rights reserved. This program and the accompanying materials
    are made available under the terms of the GNU Lesser General Public License v2.1
    which accompanies this distribution, and is available at
    https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
    
    Contributors:
        Aaron(JIN, Taeyang) - Create Main Application
"""
from crawler.newsdata import parsedriver as NewsDataParser
from crawler.opendata import parsedriver as OpenDataParser
from crawler.gwanbo import parsedriver as GwanboDriver
from crawler.jsonencoder import JsonEncoder

from multiprocessing import Pool

import datetime
import json
import os
import boto3

if __name__ == '__main__':
    gwanbo_parser = GwanboDriver.ParseDriver()

    start_date = datetime.date(2001, 1, 2)  # first: 20010102
    end_date = datetime.date(2021, 3, 11)
    date_gap = end_date - start_date

    result = []

    dates = [str(start_date + datetime.timedelta(x)).replace('-', '')
             for x in range(1, date_gap.days + 1)]

    # dates = ['20210310', '20210311']

    s3 = boto3.client(
        's3',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    f_ = os.path.join('data', '2001', '1', '3', '1319593778460000.pdf')
    bucket = 'data-portal-cdn'
    key = 'gwanbo/pdf/2001/1/3/1319593778460000.pdf'

    res = s3.upload_file(f_, bucket, key)
    print(res)

    exit()

    processing_unit = 20
    pool = Pool(processes=processing_unit)

    gwanbo_list = pool.map(gwanbo_parser.get_list_by_date, dates)

    json_directory = os.path.join('data')
    if not (os.path.isdir(json_directory)):
        os.makedirs(json_directory)
    file = os.path.join(json_directory, 'data.json')

    with open(file, 'w', encoding='utf-8') as json_file:
        json.dump(gwanbo_list, fp=json_file, ensure_ascii=False, cls=JsonEncoder)

    result = pool.map(gwanbo_parser.download_multiple_gwanbo, gwanbo_list)
    print(result)
