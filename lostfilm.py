#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib2
import HTMLParser

uid = None
passw = None
usess = None
interest = []
target_path = None

settings_file = '/home/dreamer/lostfilm.conf'
rss_url = 'http://www.lostfilm.tv/rssdd.xml'
cookies = None

link_re = re.compile('<link>(.+)</link>')
hd_re = re.compile('(\.720[pP]\.)|(\.[hH][dD]\.)')
#web_re = re.compile('\.[Ww][Ee][Bb]\.')
fullhd_re = re.compile('\.1080[pP]\.')
# filename_re = re.compile('id=.+;(.+)')
filename_re = re.compile('id=.+&(.+)')


def load_settings():
    global interest
    global cookies
    global target_path
    print 'Using options from configfile "%s":' % settings_file
    with open(settings_file) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            option = [s.strip() for s in line.split()]
            if not option:
                continue
            name = option[0].lower()
            if name == 'uid':
                if len(option) > 1:
                    uid = option[1]
                    print '... Uid: %s' % uid
            elif name == 'pass':
                if len(option) > 1:
                    passw = option[1]
                    print '... Pass: %s' % passw
            elif name == 'target_path':
                if len(option) > 1:
                    target_path = option[1]
                    print '... Target path: %s' % target_path
            elif name == 'torrent':
                if len(option) > 1:
                    is_hd = None
                    is_web = None
                    keyword = option[1]
                    for o in option[2:]:
                        o = o.lower()
                        if o == 'hd':
                            is_hd = True
                        elif o == 'sd':
                            is_hd = False
                        elif o == 'web':
                            is_web = True
                        elif o == 'noweb':
                            is_web = False
                        else:
                            print '... [WARNING] Unknown torrent option: "%s"' % o
                            continue
                    interest.append((keyword, is_hd, is_web))
                    print '... Torrent: keyword: "%s"; is HD: %s; is web: %s.' % (keyword, unicode(is_hd), unicode(is_web))
            else:
                print '[WARNING] Unknown config option "%s"' % name
    # cookies = 'uid=%s; pass=%s; usess=%s' % (uid, passw, usess)
    cookies = 'uid=%s; pass=%s' % (uid, passw)
    print cookies
    # print uid
    # print passw
    # print usess
    # print interest
    # print target_path


def load_links():
    result = []
    print 'Reading rss ...', rss_url
    response = urllib2.urlopen(
        urllib2.Request(rss_url,
                        None,
                        # {'Cookie': cookies}
                        {
                	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                            'Accept-Encoding': 'none',
                            'Accept-Language': 'en-US,en;q=0.8',
                            'Connection': 'keep-alive',
                            'Cookie': cookies }
                        )
        )
    response = response.read().decode('1251')
    # print response
    parser = HTMLParser.HTMLParser()
    return [{
            'url': unicode(parser.unescape(item)),
            'is_hd': bool(hd_re.search(item)),
            #'is_web': bool(web_re.search(item))
            'is_web': bool(not hd_re.search(item) and not fullhd_re.search(item))
            } for item in link_re.findall(response)
        ]


def download_torrent(url):
    print cookies
    print url
    file_name = filename_re.search(url).group(1)
    path = os.path.join(target_path, file_name)
    print path
    if not (os.path.exists(path) or os.path.exists(path + '.added')):
        print u'Downloading: "%s" ...' % file_name
        response = urllib2.urlopen(
            urllib2.Request(url,
                            None,
                            {
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            # 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                            #'Accept-Encoding': 'none',
                            #'Accept-Language': 'en-US,en;q=0.8',
                            #'Connection': 'keep-alive',
                            'Cookie': cookies}
                            )
        )
        print url
        torrent_content = response.read()
        print 'Length of torrent "%s" = %d ' % (file_name, len(torrent_content))
        open(path, 'wb').write(torrent_content)


def main():
    print 'LostFilm.tv torrent downloader'
    try:
        load_settings()
        links = load_links()
        print links
        for movie in interest:
            for link in links:
                if re.search(movie[0], link['url']) and (link['is_hd'] == movie[1] or movie[1] is None) and (link['is_web'] == movie[2] or movie[2] is None):
                    download_torrent(link['url'])
    except Exception as e:
        print u'[ERROR] ', unicode(e)

if __name__ == '__main__':
    main()