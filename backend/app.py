from flask import Flask, jsonify, request
from flask_cors import CORS

from valkrets import get_all_constituency
from utskott import get_all_category
from search import get_search_results, get_valkrets_id, get_utskott_id
from votering import get_all_voting, get_specific_voting

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
    return jsonify([{
        "votering_id": row[0],
        "date": row[1].strftime("%Y-%m-%d") if row[1] else None,
        "utskott": row[2],
        "valkrets_name": row[3],
        "valkrets_id": row[4]
    } for row in search_results]), 200

@app.route('/api/votering', methods=['POST'])
def votering():
    data = request.get_json()
    votering_id = data['votering_id']
    valkrets_id = data['valkrets_id']

    all_voting_results = get_all_voting(votering_id, valkrets_id)
    specific_voting_results = get_specific_voting(votering_id, valkrets_id)
    return jsonify({
        "summary": [{"rost": row[0], "count": row[1]} for row in all_voting_results],
        "details": [{"full_name": row[0], "parti_name": row[1], "rost": row[2]} for row in specific_voting_results]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)