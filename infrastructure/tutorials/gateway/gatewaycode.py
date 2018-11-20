import logging
import requests
import datetime

logger = logging.getLogger(__name__)

def get_foo():
    resp = requests.get(url="http://fooapp-service:80/")
    foo_text = resp.text
    
    ret = "foo-service returned '{}' at {}".format(foo_text, datetime.datetime.now())
    return ret
