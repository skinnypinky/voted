from flask import Flask, jsonify, request
from flask_cors import CORS

from valkrets import get_all_constituency

app = Flask(__name__)
CORS(app)

@app.route('/api/constituency', methods=['GET'])
def get_constituency():
    constituency = get_all_constituency()
    return jsonify([row[0] for row in constituency]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)