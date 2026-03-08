'''
movierulz deccandelight plugin
Copyright (C) 2016 gujal

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
import json
import re
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class mrulz(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        # Read domain from addon settings, default to .claims
        default_domain = 'https://www.5movierulz.viajes/'
        domain = self.settings('mrulz_domain') or default_domain
        self.bu = domain + '/category/'
        self.icon = self.ipath + 'mrulz.png'
        self.log('[MRULZ] __init__: Base URL set to: %s' % self.bu)
        self.log('[MRULZ] __init__: Icon path: %s' % self.icon)
        self.list = {'01Tamil Movies': self.bu + 'tamil-movie/',
                     '02Telugu Movies': self.bu + 'telugu-movie/',
                     '03Malayalam Movies': self.bu + 'malayalam-movie/',
                     '04Kannada Movies': self.bu + 'kannada-movie/',
                     '11Hindi Movies': self.bu[:-9] + 'bollywood-movie-free/',
                     '21English Movies': self.bu + 'hollywood-movie-2023/',
                     '31Tamil Dubbed Movies': self.bu + 'tamil-dubbed-movie-2/',
                     '32Telugu Dubbed Movies': self.bu + 'telugu-dubbed-movie-2/',
                     '33Hindi Dubbed Movies': self.bu + 'hindi-dubbed-movie/',
                     '34Bengali Movies': self.bu + 'bengali-movie/',
                     '35Punjabi Movies': self.bu + 'punjabi-movie/',
                     '41[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult-movie/',
                     '42[COLOR cyan]Adult 18+[/COLOR]': self.bu + 'adult-18/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        self.log('[MRULZ] get_menu: Called, returning %d categories' % len(self.list))
        return (self.list, 7, self.icon)

    def get_items(self, url):
        self.log('[MRULZ] get_items: Called with URL: %s' % url)
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Movie Rulz')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
            self.log('[MRULZ] get_items: Search query detected, updated URL: %s' % url)

        # Build headers with Cloudflare-friendly settings
        hdr = dict(self.hdr)
        hdr['Referer'] = self.bu
        
        self.log('[MRULZ] get_items: Making HTTP request with cert verification...')
        html = client.request(url, headers=hdr)
        self.log('[MRULZ] get_items: HTTP request completed')
        self.log('[MRULZ] get_items: HTML response length: %d bytes' % len(html) if html else 'None')
        
        # If standard request returns empty, try with SSL verification disabled
        # This handles misconfigured SSL certs and Cloudflare challenges
        if not html:
            self.log('[MRULZ] get_items: First attempt returned empty, retrying with SSL verification disabled...')
            hdr_no_verify = dict(hdr)
            hdr_no_verify['verifypeer'] = 'false'
            html = client.request(url, headers=hdr_no_verify)
            self.log('[MRULZ] get_items: Second attempt response length: %d bytes' % len(html) if html else 'None')
        
        if not html:
            self.log('[MRULZ] get_items: ERROR - No HTML received from server after 2 attempts!')
            self.log('[MRULZ] get_items: This may be due to Cloudflare bot detection or domain blocking.')
            return (movies, 8)
        
        self.log('[MRULZ] get_items: Parsing HTML with BeautifulSoup...')
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('nav', {'id': 'posts-nav'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'boxed film'})
        
        self.log('[MRULZ] get_items: Found %d movie items' % len(items))

        for item in items:
            title = self.unescape(item.text)
            if ')' in title:
                title = title.split(')')[0] + ')'
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Older' in str(Paginator):
            nextli = Paginator.find('div', {'class': 'nav-older'})
            purl = nextli.find('a')['href']
            pages = purl.split('/')
            currpg = int(pages[len(pages) - 2]) - 1
            title = 'Next Page.. (Currently in Page {})'.format(currpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        self.log('[MRULZ] get_videos: Called with URL: %s' % url)
        videos = []

        self.log('[MRULZ] get_videos: Making HTTP request...')
        html = client.request(url, headers=self.hdr)
        self.log('[MRULZ] get_videos: HTTP request completed, response length: %d bytes' % len(html) if html else 'None')
        
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('a')
            self.log('[MRULZ] get_videos: Found %d <a> tags in entry-content' % len(links))
            for link in links:
                vidurl = link.get('href')
                self.log('[MRULZ] get_videos: Processing link: %s' % vidurl)
                self.resolve_media(vidurl, videos)
        except Exception as e:
            self.log('[MRULZ] get_videos: Exception in <a> tag processing: %s' % str(e))
            pass

        r = re.search(r'var\s*locations\s*=\s*([^;]+)', html)
        if r:
            self.log('[MRULZ] get_videos: Found locations variable in HTML')
            links = json.loads(r.group(1))
            self.log('[MRULZ] get_videos: Parsed %d links from locations variable' % len(links))
            for link in links:
                if 'vcdnlare' in link:
                    link += '$${0}'.format(url)
                self.log('[MRULZ] get_videos: Processing location link: %s' % link)
                self.resolve_media(link, videos)
        else:
            self.log('[MRULZ] get_videos: No locations variable found in HTML')
        
        self.log('[MRULZ] get_videos: Total videos found: %d' % len(videos))
        return videos
