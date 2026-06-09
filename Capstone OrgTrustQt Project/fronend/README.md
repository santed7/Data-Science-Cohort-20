# OTQ Frontend

This folder contains a small Flask app that accepts CSV uploads, runs the OTQ v9 pipeline, and displays prediction results.

## Setup

1. Open a terminal in `Capstone OrgTrustQt Project/fronend`
2. Create and activate a virtual environment:
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run

```powershell
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Usage

Upload one or more CSV files from Slack, Teams, or Outlook. The app will parse the files, train a Ridge regression model, and display predicted response results.
