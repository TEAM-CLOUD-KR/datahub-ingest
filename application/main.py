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

if __name__ == '__main__':
    gwanbo_parser = GwanboDriver.ParseDriver()
    result = gwanbo_parser.getListByDate('20010102')

    result = gwanbo_parser.download_multiple_gwanbo(result)

    print(result)
