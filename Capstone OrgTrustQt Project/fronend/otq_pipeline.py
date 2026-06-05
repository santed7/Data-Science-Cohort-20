import io
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def parse_datetime(value: Any) -> Optional[pd.Timestamp]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, pd.Timestamp):
        ts = value
    else:
        s = str(value).strip()
        if re.fullmatch(r"\d{10}(\.\d+)?", s):
            return pd.to_datetime(float(s), unit="s", utc=True)
        ts = pd.to_datetime(s, utc=True, errors="coerce")
    if ts is pd.NaT:
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts


def load_csv_any_from_bytes(data: bytes) -> pd.DataFrame:
    text = data.decode("utf-8", errors="replace")
    return pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)


def classify(filename: str) -> Optional[str]:
    name = filename.lower()
    if "slack" in name:
        return "slack"
    if "teams" in name:
        return "teams"
    if "outlook" in name or "calendar" in name:
        return "outlook"
    return None


def parse_slack_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    ts_col = next((cols[k] for k in cols if k in ["ts", "timestamp", "time", "date"]), None)
    text_col = next((cols[k] for k in cols if k in ["text", "message", "body"]), None)
    user_col = next((cols[k] for k in cols if k in ["user", "username", "from"]), None)
    chan_col = next((cols[k] for k in cols if k in ["channel", "room", "thread"]), None)

    return pd.DataFrame({
        "source": "slack",
        "event_type": "chat",
        "timestamp": df[ts_col] if ts_col else None,
        "actor": df[user_col] if user_col else None,
        "channel": df[chan_col] if chan_col else None,
        "text": df[text_col] if text_col else None,
        "duration_min": 0.0,
        "participant_count": 2,
    })


def parse_outlook_calendar_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    subj = df[cols["subject"]] if "subject" in cols else ""
    start = df[cols.get("start", cols.get("start time", ""))] if ("start" in cols or "start time" in cols) else ""
    end = df[cols.get("end", cols.get("end time", ""))] if ("end" in cols or "end time" in cols) else ""
    org = df[cols["organizer"]] if "organizer" in cols else ""
    req = df[cols["required attendees"]] if "required attendees" in cols else ""
    opt = df[cols["optional attendees"]] if "optional attendees" in cols else ""

    def count_people(s_req: Any, s_opt: Any) -> int:
        def split_values(value: Any) -> List[str]:
            value = str(value or "").strip()
            if not value:
                return []
            return [p.strip() for p in re.split(r"[;,]", value) if p.strip()]

        return max(1, len(set(split_values(s_req) + split_values(s_opt))) + 1)

    participant_count = [count_people(r, o) for r, o in zip(req.tolist(), opt.tolist())]
    return pd.DataFrame({
        "source": "outlook",
        "event_type": "meeting",
        "timestamp": start,
        "actor": org,
        "channel": "calendar",
        "text": subj,
        "duration_min": np.nan,
        "participant_count": participant_count,
    })


def parse_teams_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    ts_col = next((cols[k] for k in cols if k in ["timestamp", "time", "date", "start", "start time", "start_time"]), None)
    subj_col = next((cols[k] for k in cols if k in ["subject", "title", "meeting subject", "name"]), None)
    org_col = next((cols[k] for k in cols if k in ["organizer", "from", "owner"]), None)
    dur_col = next((cols[k] for k in cols if k in ["duration", "duration_min", "minutes"]), None)
    part_col = next((cols[k] for k in cols if k in ["participants", "attendees", "participant_count"]), None)
    type_col = next((cols[k] for k in cols if k in ["type", "interactiontype", "event_type"]), None)

    return pd.DataFrame({
        "source": "teams",
        "event_type": df[type_col] if type_col else "teams_meeting",
        "timestamp": df[ts_col] if ts_col else None,
        "actor": df[org_col] if org_col else None,
        "channel": "teams",
        "text": df[subj_col] if subj_col else None,
        "duration_min": df[dur_col] if dur_col else 0.0,
        "participant_count": df[part_col] if part_col else 2,
    })


def parse_uploaded_csv(filename: str, data: bytes) -> pd.DataFrame:
    df = load_csv_any_from_bytes(data)
    kind = classify(filename)
    if kind == "slack":
        return parse_slack_df(df)
    if kind == "outlook":
        return parse_outlook_calendar_df(df)
    if kind == "teams":
        return parse_teams_df(df)
    return parse_teams_df(df)


def build_event_table(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    df = pd.concat(dfs, ignore_index=True)
    df["ts"] = df["timestamp"].apply(parse_datetime)
    df = df.dropna(subset=["ts"]).copy()
    df["date"] = df["ts"].dt.floor("D")
    df["duration_min"] = df["duration_min"].apply(safe_float)
    df["participant_count"] = df["participant_count"].apply(safe_int)
    df["eu"] = [
        otq_event_units(t, d, p)
        for t, d, p in zip(df["event_type"].astype(str), df["duration_min"], df["participant_count"])
    ]
    df["text_len"] = df["text"].fillna("").astype(str).str.len()
    return df


def otq_event_units(event_type: str, duration_min: float, participant_count: int) -> float:
    event_type = str(event_type or "").lower()
    base = 1.0
    if "meeting" in event_type:
        base = 3.0
    elif "chat" in event_type or "message" in event_type:
        base = 1.0
    elif "call" in event_type:
        base = 2.0
    return base * (1.0 + math.log1p(max(duration_min, 0.0))) * max(participant_count, 1)


def make_daily_features(events: pd.DataFrame) -> pd.DataFrame:
    g = events.groupby("date", as_index=False).agg(
        total_events=("eu", "size"),
        total_eu=("eu", "sum"),
        avg_eu=("eu", "mean"),
        avg_participants=("participant_count", "mean"),
        total_text=("text_len", "sum"),
        avg_duration=("duration_min", "mean"),
    )
    g["log_total_eu"] = np.log1p(g["total_eu"])
    g["log_total_events"] = np.log1p(g["total_events"])
    g["log_total_text"] = np.log1p(g["total_text"].clip(lower=0))
    return g


def compute_outcome_proxy(events: pd.DataFrame) -> pd.DataFrame:
    e = events.sort_values("ts").copy()
    e["channel_key"] = e["source"].astype(str) + "::" + e["channel"].astype(str)
    e["prev_ts"] = e.groupby("channel_key")["ts"].shift(1)
    e["delta_min"] = (e["ts"] - e["prev_ts"]).dt.total_seconds() / 60.0
    e = e[(e["delta_min"].notna()) & (e["delta_min"] > 0) & (e["delta_min"] <= 720)].copy()
    rt = e.groupby("date", as_index=False).agg(
        median_response_min=("delta_min", "median"),
        p90_response_min=("delta_min", lambda s: np.percentile(s, 90)),
        samples=("delta_min", "size"),
    )
    return rt


def fit_model(model_df: pd.DataFrame) -> Dict[str, Any]:
    feature_cols = ["log_total_eu", "log_total_events", "avg_participants", "avg_duration", "log_total_text"]
    target_col = "median_response_min"
    X = model_df[feature_cols].fillna(0.0).to_numpy()
    y = model_df[target_col].fillna(model_df[target_col].median()).to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)

    metrics = {
        "train_r2": float(r2_score(y_train, pred_train)),
        "test_r2": float(r2_score(y_test, pred_test)),
        "test_mae": float(mean_absolute_error(y_test, pred_test)),
        "samples": int(len(model_df)),
    }
    coefs = [
        {"feature": name, "coefficient": float(value)}
        for name, value in zip(feature_cols, model.coef_)
    ]
    coefs.sort(key=lambda row: abs(row["coefficient"]), reverse=True)

    return {
        "metrics": metrics,
        "coefficients": coefs,
        "model": model,
        "feature_columns": feature_cols,
    }


def run_otq_pipeline(uploaded_files: List[Any]) -> Dict[str, Any]:
    parsed_frames: List[pd.DataFrame] = []
    file_counts: Dict[str, int] = {}

    for uploaded in uploaded_files:
        if not uploaded or getattr(uploaded, "filename", "") == "":
            continue
        filename = uploaded.filename
        data = uploaded.read()
        uploaded.seek(0)
        parsed = parse_uploaded_csv(filename, data)
        parsed_frames.append(parsed)
        file_counts[filename] = int(parsed.shape[0])

    if not parsed_frames:
        raise ValueError("No valid CSV files were uploaded.")

    events = build_event_table(parsed_frames)
    if events.empty:
        raise ValueError("Uploaded files did not produce any valid event rows.")

    daily = make_daily_features(events)
    outcome = compute_outcome_proxy(events)
    model_df = daily.merge(outcome, on="date", how="inner").copy()
    if len(model_df) < 3:
        raise ValueError("Not enough merged feature/outcome rows for training. Upload more event data or more complete CSVs.")

    model_info = fit_model(model_df)
    model = model_info["model"]
    feature_cols = model_info["feature_columns"]
    predictions = model.predict(model_df[feature_cols].fillna(0.0).to_numpy())
    model_df = model_df.copy()
    model_df["predicted_response_min"] = predictions
    display_rows = model_df.sort_values("date", ascending=False).head(10)
    recent_predictions = [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "total_events": int(row["total_events"]),
            "total_eu": float(row["total_eu"]),
            "avg_participants": float(row["avg_participants"]),
            "avg_duration": float(row["avg_duration"]),
            "median_response_min": float(row["median_response_min"]),
            "predicted_response_min": float(row["predicted_response_min"]),
        }
        for _, row in display_rows.iterrows()
    ]

    # Generate simple plots and return as base64-encoded PNGs
    plots = []
    try:
        # Plot 1: EU distribution
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(events["eu"].dropna(), bins=30, color="#3366ff", edgecolor="#ffffff")
        ax.set_title("Event Units (EU) Distribution")
        ax.set_xlabel("EU")
        ax.set_ylabel("Count")
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        plots.append({"title": "EU Distribution", "data": base64.b64encode(buf.read()).decode('ascii')})

        # Plot 2: Coefficients
        coefs_df = pd.DataFrame(model_info["coefficients"])
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.barh(coefs_df['feature'], coefs_df['coefficient'], color="#2b8aef")
        ax.set_title("Feature Coefficients (sorted)")
        ax.set_xlabel("Coefficient")
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        plots.append({"title": "Feature Coefficients", "data": base64.b64encode(buf.read()).decode('ascii')})

        # Plot 3: Actual vs Predicted
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.plot(model_df['date'], model_df['median_response_min'], marker='o', label='Actual', alpha=0.8)
        ax.plot(model_df['date'], model_df['predicted_response_min'], marker='x', label='Predicted', alpha=0.9)
        ax.set_title('Actual vs Predicted Median Response (by date)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Median response (minutes)')
        ax.legend()
        fig.autofmt_xdate(rotation=25)
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png', dpi=150)
        plt.close(fig)
        buf.seek(0)
        plots.append({"title": "Actual vs Predicted", "data": base64.b64encode(buf.read()).decode('ascii')})
    except Exception as e:
        # If plotting fails, include the error message in the result
        plots.append({"title": "plots_error", "data": str(e)})

    return {
        "file_counts": file_counts,
        "event_rows": int(events.shape[0]),
        "daily_rows": int(daily.shape[0]),
        "outcome_rows": int(outcome.shape[0]),
        "model_rows": int(model_df.shape[0]),
        "metrics": model_info["metrics"],
        "coefficients": model_info["coefficients"],
        "recent_predictions": recent_predictions,
        "plots": plots,
    }
