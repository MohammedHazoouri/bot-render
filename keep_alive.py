import threading
from web import app
import os
def run():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()