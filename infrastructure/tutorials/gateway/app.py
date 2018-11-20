import logging

from flask import Flask

import gatewaycode

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def root():
    ret = gatewaycode.get_foo()
    return ret
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)