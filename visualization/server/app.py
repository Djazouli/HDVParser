from flask import Flask, jsonify, abort
from flask_cors import CORS
from database.utils import get_items, get_item_prices

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/items_list', methods=['GET'])
def get_items_list():
    return jsonify(get_items())

@app.route('/item/<item_id>')
def get_item_data(item_id: int=None):
    if item_id is None:
        abort(404)
    return jsonify(get_item_prices(item_id))

if __name__ == '__main__':
    app.run()