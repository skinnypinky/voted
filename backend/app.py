from flask import Flask, jsonify, request
from flask_cors import CORS

from valkrets import get_all_constituency
from utskott import get_all_category
from search import get_search_results, get_valkrets_id, get_utskott_id

app = Flask(__name__)
CORS(app)

@app.route('/api/constituency', methods=['GET'])
def get_constituency():
    constituency = get_all_constituency()
    return jsonify([row[0] for row in constituency]), 200

@app.route('/api/utskott', methods=['GET'])
def get_utskott():
    utskott = get_all_category()
    return jsonify([row[0] for row in utskott]), 200

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    valkrets_name = data['valkrets']
    utskott_name = data['utskott']

    valkrets_id = get_valkrets_id(valkrets_name)
    utskott_id = get_utskott_id(utskott_name)

    if valkrets_id is None or utskott_id is None:
        return jsonify([]), 200

    search_results = get_search_results(valkrets_id, utskott_id)
    return jsonify([row[0] for row in search_results]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)