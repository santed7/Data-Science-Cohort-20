from flask import Flask, redirect, render_template, request, url_for

from otq_pipeline import run_otq_pipeline

app = Flask(__name__, template_folder="templates")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
