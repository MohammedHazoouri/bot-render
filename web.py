from flask import Flask
app = Flask(__name__)
@app.route("/")
def index():
    return "Bot is running", 200
if __name__ == "main":
         app.run(host="0.0.0.0", port=8000)