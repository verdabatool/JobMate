from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend_jobs_from_input
from data_loader import load_all_jobs

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for testing

@app.route("/jobs")
def get_jobs():
    df = load_all_jobs()
    return jsonify(df.to_dict(orient="records"))

@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    data = request.json
    job_title = data.get("job_title", "")
    preferences = data.get("preferences", "")
    top_n = data.get("top_n", 5)

    if not job_title or not preferences:
        return jsonify({"error": "job_title and preferences required"}), 400

    results = recommend_jobs_from_input(job_title, preferences, top_n)
    return jsonify({"recommendations": results})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)
