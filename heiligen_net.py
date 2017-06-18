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
import model
import bs4
import zlib
from lxml import html
import cookielib


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
                try:
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
                except AttributeError:
                    logging.warning("No complete data found on %s" % item_url)
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



# following code is copied from catecheserooster project
def element_to_json(e):
    # transform a single element
    # returns a tuple tag,content,tail where
    # - tag is the name of the element
    # - content is a dict with the element's attributes and child elements
    #   (merged into arrays if appropriate)
    # - tail is the content of a text node child of the parent that comes
    #   right after this element (actually belongs to the parent)
    content = {}  # empty JSON object
    is_text_node = True
    for attribute_name in e.attrib:
        is_text_node = False
        # an attribute becomes a key,value property in JSON
        content[attribute_name] = e.attrib[attribute_name]
    # a text node that comes before the first child element
    # goes into the content property
    content["content"] = e.text
    for child in e:
        is_text_node = False
        child_tag, child_content, child_tail = element_to_json(child)
        if child_tag in content:
            if type(content[child_tag]) is list:
                # a child element with a name that already occurred
                # is appended to the key,value array property in JSON
                # with that name
                content[child_tag].append(child_content)
            else:
                # if it's the second child element with that name,
                # the array must be constructed
                content[child_tag] = [content[child_tag], child_content]
        else:
            # a child element becomes a key,value property in JSON
            content[child_tag] = child_content
        # a text node that comes right after this element
        # goes into the content property
        if child_tail:
            if content["content"]:
                content["content"] += child_tail
            else:
                content["content"] = child_tail
    if is_text_node:
        return e.tag, content["content"], ''
    else:
        return e.tag, content, e.tail


def elements_list_to_json(l):
    # the query result can be a list of elements and strings
    # returns the content where
    # - content is a dict with the child elements (merged into arrays if appropriate)
    #   and a 'content' property containing the strings concatenated
    # OR
    # - just the strings concatenated if there were no elements
    content = {}  # empty JSON object
    is_only_text = True
    content["content"] = ""
    for child in l:
        if isinstance(child, basestring):
            content["content"] += child
        else:
            is_only_text = False
            child_tag, child_content, child_tail = element_to_json(child)
            if child_tag in content:
                if type(content[child_tag]) is list:
                    # a child element with a name that already occurred
                    # is appended to the key,list-of-value array property in JSON
                    # with that name
                    content[child_tag].append(child_content)
                else:
                    # if it's the second child element with that name,
                    # the array must be constructed
                    content[child_tag] = [content[child_tag], child_content]
            else:
                # a child element becomes a key,value property in JSON
                content[child_tag] = child_content
    if is_only_text:
        return content["content"]
    else:
        return content


def getHtml(url, xpath):
    """
     return the result as a json dict; if the xpath queries for an <a> element, access the result as {'a':...}
     or {'a':[...]} if more than one match
    """
    logging.info("Going to query %s for %s." % (url, xpath))
    sleep = 1
    for attempt in range(10):
        try:
            logging.info("Querying %s." % url)
            hdr = {
                "Accept-Language": "en-US,en;q=0.5",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "http://thewebsite.com",
                "Connection": "keep-alive"
            }
            request = urllib2.Request(url, headers=hdr)
            htmlstring = urllib2.urlopen(request).read()
            tree = html.fromstring(htmlstring)
            result = tree.xpath(xpath)
        except (httplib.HTTPException, apiproxy_errors.DeadlineExceededError) as e:
            time.sleep(sleep)  # pause to avoid "Rate Limit Exceeded" error
            logging.warning("Sleeping %d seconds because of HttpError trying to query %s (%s)." % (sleep, url, e))
            sleep *= 2
        else:
            break  # no error caught
    else:
        logging.critical("Retried 10 times querying %s." % url)
        raise  # attempts exhausted
    return elements_list_to_json(result)


