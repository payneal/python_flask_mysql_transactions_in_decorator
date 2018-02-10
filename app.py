from flask import Flask
from app2 import create_app
from database import mysqlConnectorPool

# you run
app = Flask(__name__)

if __name__ == '__main__':
    # global holder
    db_connection = mysqlConnectorPool()
    # see create_app
    app = create_app(db_connection)
    app.run(debug=True, threaded=True)