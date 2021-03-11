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

from multiprocessing import Pool

import datetime

if __name__ == '__main__':
    gwanbo_parser = GwanboDriver.ParseDriver()

    start_date = datetime.date(2001, 1, 2)  # first: 20010102
    end_date = datetime.date(2021, 3, 10)
    date_gap = end_date - start_date

    result = []

    dates = [str(start_date + datetime.timedelta(x)).replace('-', '')
             for x in range(1, date_gap.days + 1)]

    dates = ['20210311']

    processing_unit = 20
    pool = Pool(processes=processing_unit)

    # for date in dates:
    #     gwanbo_parser.get_list_by_date(date)
    #
    gwanbo_list = pool.map(gwanbo_parser.get_list_by_date, dates)
    print(len(gwanbo_list))
    pool.map(gwanbo_parser.download_multiple_gwanbo, gwanbo_list)
