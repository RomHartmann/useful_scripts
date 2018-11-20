import logging

from flask import Flask

import mycode

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def root():
    ret = mycode.test_func()
    return ret
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)