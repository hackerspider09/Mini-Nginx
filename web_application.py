from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Web app => Hello World"

@app.route("/api")
def api():
    return "Web app => /api"

if __name__ == "__main__":
    app.run(port=5000)
