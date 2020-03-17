# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    import sys

    host = sys.argv[1]
    port = sys.argv[2]
    port = int(port)
    print(host, port)
    app.run(host=host, port=port, debug=True)
