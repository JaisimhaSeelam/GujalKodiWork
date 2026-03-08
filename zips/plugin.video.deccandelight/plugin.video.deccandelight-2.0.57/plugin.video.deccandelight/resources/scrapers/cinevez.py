'''
DeccanDelight scraper plugin
Copyright (C) 2021 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import control, client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class cinevez(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.cinevez.foo/language/'
        self.icon = self.ipath + 'cinevez.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil/',
                     '02Telugu Movies': self.bu + 'telugu/',
                     '03Malayalam Movies': self.bu + 'malayalam/',
                     '04Kannada Movies': self.bu + 'kannada/',
                     '05Hindi Movies': self.bu + 'hindi/',
                     '06English Movies': self.bu + 'english/',
                     '07Dubbed Movies': self.bu + 'dubbed/',
                     '98[COLOR cyan]Adult Movies[/COLOR]': self.bu[:-9] + 'rating/18/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Cinevez')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = client.request(url)
        mlink = SoupStrainer('div', {'class': re.compile('^main')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        soup = BeautifulSoup(html, "html.parser")
        items = mdiv.find_all('div', {'class': 'post-item'})

        for item in items:
            title = self.unescape(item.find('h2').text)
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('h2').parent.get('href')
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        paginator = soup.find('div', {'class': re.compile(r'\bpagination\b')})
        if not paginator:
            paginator = soup.find('div', {'class': re.compile(r'\bwp-pagenavi\b')})
        if not paginator:
            paginator = soup.find('nav')

        next_link = None
        if paginator:
            next_link = paginator.find('a', {'rel': 'next'})
            if not next_link:
                next_link = paginator.find('a', {'class': re.compile(r'\b(next|nextpostslink)\b')})
            if not next_link:
                next_link = paginator.find('a', string=re.compile(r'(Next|Older|»)', re.I))

        if not next_link:
            next_link = soup.find('a', {'rel': 'next'})
        if not next_link:
            next_link = soup.find('a', string=re.compile(r'(Next|Older|»)', re.I))

        if next_link and next_link.get('href'):
            purl = next_link.get('href')
            currpg = '1'
            curr = paginator.find(['a', 'span'], {'class': re.compile(r'(bg-primary|current)')}) if paginator else None
            if curr and curr.text:
                currpg = curr.text.strip()
            else:
                m = re.search(r'/page/(\d+)', url)
                if m:
                    currpg = m.group(1)

            lastpg = '?'
            if paginator:
                nums = paginator.find_all('a', {'class': re.compile(r'page-numbers')})
                if len(nums) >= 2:
                    lastpg = nums[-2].text.strip()
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = client.request(url)
        if '/series' in url:
            surl = ''
            seasons = re.findall('<a.+?href="([^"]+/season/[^"]+)">(?:<h2>)?([^<]+)', html)
            if len(seasons) == 1:
                surl = seasons[0][0]
            elif len(seasons) > 1:
                ret = control.select('Choose Season',
                                     [self.unescape(item[1]).encode('utf-8') if self.PY2 else self.unescape(item[1])
                                      for item in seasons])
                if ret != -1:
                    surl = seasons[ret][0]
            if surl:
                html = client.request(surl)

        magnets = re.findall('<a.+?href="(magnet[^"]+)', html)
        if magnets:
            for magnet in magnets:
                self.resolve_media(magnet, videos)

        links = re.findall('<a.+?href="([^"]+)">Download', html)
        if links:
            for link in links:
                self.resolve_media(link, videos)

        return videos
