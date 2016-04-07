# this one is added here to avoid spending a separate app on it
import webapp2
from jinja_templates import jinja_environment
import urllib2
import time
import datetime
import cgi
import logging
import httplib
from google.appengine.runtime import apiproxy_errors
import json
import urllib
import bs4  # library included especially for this...
import model
import zlib


class HeiligenNetHandler(webapp2.RequestHandler):
    def get(self):
        key = 'heiligen'
        # query the cache
        cache = model.Heiligen_cache.get_or_insert(key)
        if cache.content and cache.date == datetime.date.today():
            output = zlib.decompress(cache.content).decode('unicode_escape')
        else:
            url = "http://heiligen.net/heiligen_dag.php?MD=%s" % time.strftime("%m%d")
            xpath = "(//div[@id='inhoud']//table)[1]//td[2]/a"
            harvest = getHtml(url, xpath)
            items = []
            for a in harvest['a']:
                item_url = "http://heiligen.net" + a['href']
                html = urllib2.urlopen(item_url).read()
                # html isn't pretty, so using beautifulsoup for parsing i.o. ElementTree
                soup = bs4.BeautifulSoup(html)
                title = soup.find('title').text
                content = soup.find('div', id='inhoud').prettify()
                items.append({
                    'title': title,
                    'description': cgi.escape(content),
                    'url': item_url
                })
            date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
            midnight = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
            long_date_midnight = datetime.datetime.strftime(midnight, "%a, %d %b %Y %H:%M:%S +0000")
            long_date = datetime.datetime.strftime(datetime.datetime.now(), "%a, %d %b %Y %H:%M:%S +0000")
            template = jinja_environment.get_template('heiligen-net.rss')
            output = template.render(
                items=items,
                date=date,
                url=url,
                long_date=long_date,
                long_date_midnight=long_date_midnight
            )
            # update cache
            cache.content = zlib.compress(output.encode('unicode_escape'))
            cache.date = datetime.date.today()
            cache.put()
        # return the web-page content
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % 900
        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.out.write(output)


def getHtml(url, xpath):
    """
     return the result as a json dict; if the xpath queries for an <a> element, access the result as {'a':...}
     or {'a':[...]} if more than one match
     THIS IS CODE COPIED FROM THE catecheserooster GAE PROJECT IN data.py
    """
    yql = 'select * from html where url="%s" and xpath="%s" and compat="html5"' % (url, xpath)
    query = "http://query.yahooapis.com/v1/public/yql?q=%s&format=json" % urllib.quote_plus(yql)
    logging.info("Going to query %s for %s [%s][%s]." % (url, xpath, yql, query))
    sleep = 1
    for attempt in range(10):
        try:
            logging.info("Querying %s." % url)
            result = urllib2.urlopen(query).read()
        except (httplib.HTTPException, apiproxy_errors.DeadlineExceededError) as e:
            time.sleep(sleep)  # pause to avoid "Rate Limit Exceeded" error
            logging.warning("Sleeping %d seconds because of HttpError trying to query %s (%s)." % (sleep, url, e))
            sleep *= 2
        else:
            break  # no error caught
    else:
        logging.critical("Retried 10 times querying %s." % url)
        raise  # attempts exhausted
    return json.loads(result)['query']['results']
