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

import datetime

if __name__ == '__main__':
    gwanbo_parser = GwanboDriver.ParseDriver()

    start_date = datetime.date(2001, 1, 2)
    end_date = datetime.date(2021, 3, 10)
    date_gap = end_date - start_date
    print(date_gap.days)

    for i in range(date_gap.days+1):
        curr_date = start_date + datetime.timedelta(i)
        print(curr_date)
    #     print(item)

    # result = gwanbo_parser.getListByDate('20010102')
    # result = gwanbo_parser.download_multiple_gwanbo(result)
    # print(result)
