"""
    Copyright (c) 2021 Aaron(JIN, Taeyang).
    All rights reserved. This program and the accompanying materials
    are made available under the terms of the GNU Lesser General Public License v2.1
    which accompanies this distribution, and is available at
    http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
    
    Contributors:
        Aaron(JIN, Taeyang) - Create Main Application
"""
from crawler.newsdata import parsedriver as NewsDataParser
from crawler.opendata import parsedriver as OpenDataParser

if __name__ == '__main__':
    news_data_parser = NewsDataParser.ParseDriver()
    open_data_parser = OpenDataParser.ParseDriver()
    print(news_data_parser.agent)
    print(open_data_parser.agent)
