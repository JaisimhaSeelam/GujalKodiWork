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
import sys
from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse, urllib_request, urllib_error


class mrulz(Scraper):
    # List of alternative domains to try if main domain fails
    KNOWN_DOMAINS = [
        'https://www.5movierulz.viajes',
        'https://www.5movierulz.claims',
        'https://www.5movierulz.travel',
        'https://www.4movierulz.ph'
    ]
    
    def __init__(self):
        Scraper.__init__(self)
        # Read domain from addon settings, default to .viajes
        default_domain = 'https://www.5movierulz.viajes'
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
    
    def make_raw_request(self, url, headers, retry_http=False):
        """Make a raw HTTP request with detailed error logging."""
        protocol = "HTTP" if url.startswith('http://') else "HTTPS"
        self.log('[MRULZ] make_raw_request: Attempting raw %s request to %s' % (protocol, url))
        try:
            req = urllib_request.Request(url)
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            response = urllib_request.urlopen(req, timeout=20)
            html = response.read()
            response.close()
            self.log('[MRULZ] make_raw_request: SUCCESS - Got %d bytes' % len(html))
            return html.decode('utf-8', errors='ignore') if isinstance(html, bytes) else html
        except urllib_error.HTTPError as e:
            self.log('[MRULZ] make_raw_request: HTTPError %d - %s' % (e.code, e.reason))
            self.log('[MRULZ] make_raw_request: Error headers: %s' % str(e.headers))
            try:
                content = e.read()
                self.log('[MRULZ] make_raw_request: Error body length: %d bytes' % len(content))
                return content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else content
            except:
                return None
        except urllib_error.URLError as e:
            self.log('[MRULZ] make_raw_request: URLError - %s' % str(e.reason))
            # If HTTPS fails with SSL error, try HTTP as fallback
            if 'SSL' in str(e.reason) and url.startswith('https://') and not retry_http:
                self.log('[MRULZ] make_raw_request: SSL error detected, retrying with HTTP...')
                http_url = url.replace('https://', 'http://', 1)
                return self.make_raw_request(http_url, headers, retry_http=True)
            return None
        except Exception as e:
            self.log('[MRULZ] make_raw_request: Unexpected error - %s: %s' % (type(e).__name__, str(e)))
            return None

    def get_menu(self):
        self.log('[MRULZ] get_menu: Called, returning %d categories' % len(self.list))
        return (self.list, 7, self.icon)

    def fetch_html(self, url, hdr):
        """Fetch HTML from URL with multiple fallback strategies. Returns (html, success_url)."""
        self.log('[MRULZ] fetch_html: Fetching from %s' % url)
        
        # Try to get extended response info to diagnose issues
        self.log('[MRULZ] fetch_html: Making HTTP request with cert verification (extended mode)...')
        try:
            response_data = client.request(url, headers=hdr, output='extended')
            if response_data:
                html, code, response_headers, request_headers, cookies, final_url = response_data
                self.log('[MRULZ] fetch_html: HTTP response code: %s' % code)
                self.log('[MRULZ] fetch_html: Response content length: %d bytes' % len(html) if html else '0')
                if html:
                    return (html, url)
            else:
                self.log('[MRULZ] fetch_html: Extended request returned None')
        except Exception as e:
            self.log('[MRULZ] fetch_html: Exception during extended request: %s' % str(e))
        
        # If standard request returns empty, try with SSL verification disabled
        self.log('[MRULZ] fetch_html: First attempt returned empty, retrying with SSL verification disabled...')
        hdr_no_verify = dict(hdr)
        hdr_no_verify['verifypeer'] = 'false'
        try:
            response_data = client.request(url, headers=hdr_no_verify, output='extended')
            if response_data:
                html, code, response_headers, request_headers, cookies, final_url = response_data
                self.log('[MRULZ] fetch_html: Retry HTTP response code: %s' % code)
                self.log('[MRULZ] fetch_html: Retry response content length: %d bytes' % len(html) if html else '0')
                if html:
                    return (html, url)
            else:
                self.log('[MRULZ] fetch_html: Retry extended request returned None')
        except Exception as e:
            self.log('[MRULZ] fetch_html: Exception during retry request: %s' % str(e))
        
        # Third attempt: try raw urllib request with minimal setup to get diagnostic info
        self.log('[MRULZ] fetch_html: Second attempt returned empty, trying raw urllib request for diagnostics...')
        html = self.make_raw_request(url, hdr)
        if html:
            return (html, url)
        
        self.log('[MRULZ] fetch_html: FAILED - No HTML received after 3 attempts for %s' % url)
        return (None, None)

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
        
        # Try to fetch HTML from primary domain
        html, success_url = self.fetch_html(url, hdr)
        
        # If primary domain fails, try alternative domains
        if not html:
            self.log('[MRULZ] get_items: Primary domain failed, trying alternative domains...')
            primary_base = self.bu[:-9]  # Remove '/category/'
            
            for alt_domain in self.KNOWN_DOMAINS:
                # Skip the domain we already tried
                if alt_domain in primary_base:
                    continue
                
                alt_url = url.replace(primary_base, alt_domain + '/', 1)
                self.log('[MRULZ] get_items: Trying alternative domain: %s' % alt_url)
                html, success_url = self.fetch_html(alt_url, hdr)
                
                if html:
                    self.log('[MRULZ] get_items: SUCCESS with alternative domain: %s' % alt_domain)
                    # Update base URL for consistency
                    self.bu = alt_domain + '/category/'
                    break
        
        if not html:
            self.log('[MRULZ] get_items: ERROR - No HTML received from any domain!')
            self.log('[MRULZ] get_items: Issue may be Cloudflare bot detection, SSL errors, or domain unavailability.')
            self.log('[MRULZ] get_items: Try changing domain in addon settings: Settings → Movie Rulz Settings')
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
