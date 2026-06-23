from flask import Flask, jsonify, redirect, render_template, request, url_for

import otq_pipeline
from otq_pipeline import PIPELINE_BUILD, run_otq_pipeline

app = Flask(__name__, template_folder="templates")


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/debug-pipeline", methods=["GET"])
def debug_pipeline():
    return jsonify({
        "pipeline_build": PIPELINE_BUILD,
        "pipeline_file": otq_pipeline.__file__,
        "eda_renderer": "PNG",
        "model_diagnostics_renderer": "PNG",
    })


@app.route("/predict", methods=["POST"])
def predict():
    files = request.files.getlist("files")
    if not files or all(getattr(file, "filename", "") == "" for file in files):
        return render_template("index.html", error="Please upload at least one CSV file.")

    try:
        result = run_otq_pipeline(files)
    except Exception as exc:
        return render_template("index.html", error=str(exc))

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
