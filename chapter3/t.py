from datetime import datetime, timedelta
import feedparser
import re
import time

readme = open('dsdata.txt').read()
feeds = re.findall('\* (.*?) http([s]{0,1})\:\/\/(.*?) \[\(RSS\)\]\((.*?)\)', readme)

out = open('dsdata1.txt', 'w', encoding='utf-8')
out.write('Blog')
for url in feeds:
    out.write('\t%s' % url[3].strip())
    out.write('\n')
