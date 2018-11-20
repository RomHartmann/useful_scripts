import logging
import requests

from flask import Flask, request

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def root():
    ret_text = """
    <h1>oAuth proxy server</h1>
    <h3>From http://oauthbin.com/</h3>
    <p>This is just a wrapper around their service so that we can test it against https.</p>
    <p>(This is just their home page plagarized for help text purposes)</p>
    <h1>---</h1>
    """
    resp = requests.get("http://oauthbin.com/")
    ret_text += resp.text
    return ret_text


@app.route("/v1/request-token", methods=['GET'])
def request_token():
    params = request.args
    resp = requests.get(
        url="http://oauthbin.com/v1/request-token",
        params=params
    )
    ret = resp.text
    return ret


@app.route("/v1/access-token", methods=['GET'])
def access_token():
    params = request.args
    resp = requests.get(
        url="http://oauthbin.com/v1/access-token",
        params=params
    )
    ret = resp.text
    return ret


@app.route("/v1/echo", methods=['GET'])
def echo():
    params = request.args
    resp = requests.get(
        url="http://oauthbin.com/v1/echo",
        params=params
    )
    ret = resp.text
    return ret

 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)