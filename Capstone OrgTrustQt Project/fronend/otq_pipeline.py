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
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from sklearn.linear_model import Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.inspection import permutation_importance
import base64

PIPELINE_BUILD = "2026-06-19-matplotlib-dashboard-v4"
PLOT_CONFIG = {"responsive": True, "displayModeBar": False}


def plotly_fragment(fig: go.Figure) -> str:
    return pio.to_html(
        fig,
        include_plotlyjs=False,
        full_html=False,
        config=PLOT_CONFIG,
        default_width="100%",
    )


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

    if "meeting" in event_type or "teams_meeting" in event_type:
        base = 24.5
    elif "call" in event_type or "phone" in event_type:
        base = 8.5
    elif "email" in event_type or "outlook" in event_type:
        base = 6.0
    elif "chat" in event_type or "message" in event_type or "slack" in event_type:
        base = 9.5
    else:
        base = 5.0

    dur_bonus = min(max(duration_min, 0.0), 120.0) / 60.0
    participant_bonus = math.log(max(participant_count, 1), 2) * 1.5
    return float(base + dur_bonus + participant_bonus)


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
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "pred_train": pred_train,
        "pred_test": pred_test,
    }


def make_eda_plots(events: pd.DataFrame, daily: pd.DataFrame, outcome: pd.DataFrame) -> str:
    """Generate 6 EDA subplots as a single Plotly subplot figure."""
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=("EU Score Distribution", "log(Duration) Distribution",
                       "Participant Count Distribution", "EU by Event Type",
                       "Daily Total EU Over Time", "EU vs Median Response Time"),
        specs=[[{}, {}, {}], [{}, {}, {}]],
        horizontal_spacing=0.12,
        vertical_spacing=0.18
    )
    
    # Plot 1: EU distribution
    fig.add_trace(go.Histogram(x=events["eu"].dropna(), nbinsx=30, name="EU", marker_color="#3366ff"),
                  row=1, col=1)
    
    # Plot 2: Duration distribution (log scale)
    dur_nonzero = events.loc[events["duration_min"] > 0, "duration_min"]
    fig.add_trace(go.Histogram(x=np.log1p(dur_nonzero), nbinsx=30, name="log(Duration)", marker_color="#ff6b6b"),
                  row=1, col=2)
    
    # Plot 3: Participant count
    fig.add_trace(go.Histogram(x=events["participant_count"], nbinsx=15, name="Participants", marker_color="#51cf66"),
                  row=1, col=3)
    
    # Plot 4: EU by event type (boxplot)
    for event_type in events["event_type"].dropna().unique():
        subset = events[events["event_type"] == event_type]["eu"]
        fig.add_trace(go.Box(y=subset, name=event_type, boxmean="sd"), row=2, col=1)
    
    # Plot 5: Daily total EU over time
    daily_sorted = daily.sort_values("date")
    fig.add_trace(go.Scatter(x=daily_sorted["date"], y=daily_sorted["total_eu"], 
                            mode="lines", name="Daily EU", line=dict(color="#3366ff")),
                  row=2, col=2)
    
    # Plot 6: EU vs response time scatter
    merged = daily.merge(outcome, on="date", how="inner")
    fig.add_trace(go.Scatter(x=merged["total_eu"], y=merged["median_response_min"],
                            mode="markers", name="EU vs Response", marker=dict(color="#ff9500")),
                  row=2, col=3)
    
    fig.update_xaxes(title_text="EU", row=1, col=1)
    fig.update_xaxes(title_text="log(Duration)", row=1, col=2)
    fig.update_xaxes(title_text="# Participants", row=1, col=3)
    fig.update_xaxes(title_text="Event Type", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_xaxes(title_text="Total EU", row=2, col=3)
    
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=3)
    fig.update_yaxes(title_text="EU", row=2, col=1)
    fig.update_yaxes(title_text="Total EU", row=2, col=2)
    fig.update_yaxes(title_text="Median Response (min)", row=2, col=3)
    
    fig.update_layout(
        height=760,
        showlegend=False,
        title_text="Exploratory Data Analysis (EDA)",
        margin=dict(l=70, r=35, t=95, b=75),
        template="plotly_white",
        font=dict(size=11),
    )
    fig.update_annotations(font_size=12)
    return plotly_fragment(fig)


def make_eda_plots_png(events: pd.DataFrame, daily: pd.DataFrame, outcome: pd.DataFrame) -> str:
    """Notebook cell 23: six-panel EDA rendered as a PNG."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("EDA - Feature Distributions", fontsize=14, fontweight="bold")

    axes[0, 0].hist(events["eu"].dropna(), bins=30, color="steelblue", edgecolor="white")
    axes[0, 0].set_title("EU Score Distribution")
    axes[0, 0].set_xlabel("Event Units (EU)")
    axes[0, 0].set_ylabel("Count")

    dur_nonzero = events.loc[events["duration_min"] > 0, "duration_min"].dropna()
    if len(dur_nonzero) > 0:
        axes[0, 1].hist(np.log1p(dur_nonzero), bins=30, color="coral", edgecolor="white")
    else:
        axes[0, 1].text(0.5, 0.5, "No non-zero durations", ha="center", va="center", transform=axes[0, 1].transAxes)
    axes[0, 1].set_title("log(Duration + 1) Distribution")
    axes[0, 1].set_xlabel("log(minutes + 1)")
    axes[0, 1].set_ylabel("Count")

    participant_max = max(15, int(events["participant_count"].max()) + 2)
    axes[0, 2].hist(events["participant_count"].dropna(), bins=range(1, participant_max), color="mediumseagreen", edgecolor="white")
    axes[0, 2].set_title("Participant Count Distribution")
    axes[0, 2].set_xlabel("# Participants")
    axes[0, 2].set_ylabel("Count")

    event_order = events.groupby("event_type")["eu"].median().sort_values(ascending=False).index
    sns.boxplot(data=events, x="event_type", y="eu", order=event_order, ax=axes[1, 0], palette="muted")
    axes[1, 0].set_title("EU Score by Event Type")
    axes[1, 0].set_xlabel("Event Type")
    axes[1, 0].set_ylabel("EU Score")
    axes[1, 0].tick_params(axis="x", rotation=15)

    daily_sorted = daily.sort_values("date")
    axes[1, 1].plot(daily_sorted["date"], daily_sorted["total_eu"], color="steelblue", linewidth=1.2)
    axes[1, 1].set_title("Daily Total EU Over Time")
    axes[1, 1].set_xlabel("Date")
    axes[1, 1].set_ylabel("Total EU")
    axes[1, 1].tick_params(axis="x", rotation=30)

    merged_eda = daily.merge(outcome, on="date", how="inner")
    if len(merged_eda) > 0:
        axes[1, 2].scatter(
            merged_eda["total_eu"],
            merged_eda["median_response_min"],
            alpha=0.6,
            color="darkorange",
            edgecolors="white",
            linewidths=0.5,
        )
    else:
        axes[1, 2].text(0.5, 0.5, "No merged outcome rows", ha="center", va="center", transform=axes[1, 2].transAxes)
    axes[1, 2].set_title("Total EU vs Median Response Time")
    axes[1, 2].set_xlabel("Total EU (daily)")
    axes[1, 2].set_ylabel("Median Response (min)")

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def make_correlation_heatmap(daily: pd.DataFrame) -> str:
    """Generate correlation heatmap as Plotly."""
    corr_cols = ["total_eu", "total_events", "avg_eu", "avg_participants", "avg_duration",
                 "log_total_eu", "log_total_events", "log_total_text"]
    available_cols = [c for c in corr_cols if c in daily.columns]
    if not available_cols:
        raise ValueError("No daily feature columns are available for the correlation heatmap.")

    corr_input = daily[available_cols].apply(pd.to_numeric, errors="coerce")
    corr_matrix = corr_input.corr()

    # Correlation is undefined for one-row data or zero-variance columns.
    # Keep the heatmap visible by showing undefined off-diagonal values as 0
    # and self-correlation as 1.
    corr_matrix = corr_matrix.reindex(index=available_cols, columns=available_cols)
    corr_values = corr_matrix.to_numpy(dtype=float)
    corr_values = np.nan_to_num(corr_values, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(corr_values, 1.0)
    text_values = np.round(corr_values, 2)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_values,
        x=available_cols,
        y=available_cols,
        colorscale="RdBu",
        zmid=0,
        zmin=-1,
        zmax=1,
        text=text_values,
        texttemplate="%{text:.2f}",
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    fig.update_layout(
        title="Feature Correlation Matrix (Daily Aggregated)",
        height=650,
        margin=dict(l=155, r=35, t=75, b=120),
        template="plotly_white",
        font=dict(size=11),
    )
    fig.update_xaxes(type="category", tickangle=-35)
    fig.update_yaxes(type="category", autorange="reversed")
    return plotly_fragment(fig)


def make_correlation_heatmap_png(daily: pd.DataFrame) -> str:
    """Notebook cell 24: seaborn correlation heatmap rendered as PNG."""
    corr_cols = ["total_eu", "total_events", "avg_eu", "avg_participants", "avg_duration",
                 "log_total_eu", "log_total_events", "log_total_text"]
    available_cols = [c for c in corr_cols if c in daily.columns]
    if not available_cols:
        raise ValueError("No daily feature columns are available for the correlation heatmap.")

    corr_input = daily[available_cols].apply(pd.to_numeric, errors="coerce")
    corr_matrix = corr_input.corr().reindex(index=available_cols, columns=available_cols)
    corr_values = corr_matrix.to_numpy(dtype=float)
    corr_values = np.nan_to_num(corr_values, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(corr_values, 1.0)
    corr_display = pd.DataFrame(corr_values, index=available_cols, columns=available_cols)

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr_display,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        ax=ax,
        square=True,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Feature Correlation Matrix\n(Daily Aggregated Features)", fontsize=13, fontweight="bold")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def make_source_channel_breakdown(events: pd.DataFrame) -> str:
    """Notebook cell 25: events by source and total EU by channel."""
    from plotly.subplots import make_subplots

    source_counts = events["source"].value_counts()
    channel_eu = events.groupby("channel")["eu"].sum().sort_values(ascending=True)

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Events by Source", "Total EU by Channel"),
        horizontal_spacing=0.20,
        specs=[[{}, {}]],
    )
    fig.add_trace(
        go.Bar(
            x=source_counts.index,
            y=source_counts.values,
            text=source_counts.values,
            textposition="outside",
            marker_color=["#4682b4", "#ff7f50", "#3cb371"][: len(source_counts)],
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=channel_eu.values,
            y=channel_eu.index,
            orientation="h",
            marker_color="#6a5acd",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.update_xaxes(title_text="Source", row=1, col=1)
    fig.update_yaxes(title_text="Event Count", row=1, col=1)
    fig.update_xaxes(title_text="Total EU Score", row=1, col=2)
    fig.update_yaxes(title_text="Channel", row=1, col=2)
    fig.update_layout(
        height=500,
        title_text="Communication Source & Event Type Breakdown",
        margin=dict(l=110, r=35, t=90, b=70),
        template="plotly_white",
        font=dict(size=11),
    )
    fig.update_annotations(font_size=12)
    return plotly_fragment(fig)


def make_alpha_sweep_plot(X: np.ndarray, y: np.ndarray) -> str:
    """Notebook cell 31: Ridge alpha sweep with CV RMSE error bars."""
    alphas = np.logspace(-3, 3, 13)
    mean_rmse = np.zeros(len(alphas))
    std_rmse = np.zeros(len(alphas))

    for i, alpha in enumerate(alphas):
        folds = cv_rmse(Ridge(alpha=alpha), X, y)
        mean_rmse[i] = np.nanmean(folds)
        std_rmse[i] = np.nanstd(folds)

    best_idx = int(np.nanargmin(mean_rmse))
    best_alpha = float(alphas[best_idx])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=alphas,
            y=mean_rmse,
            error_y=dict(type="data", array=std_rmse, visible=True),
            mode="lines+markers",
            name="CV RMSE",
            line=dict(color="#4682b4"),
        )
    )
    fig.add_vline(
        x=best_alpha,
        line_dash="dash",
        line_color="#b22222",
        annotation_text=f"best alpha = {best_alpha:g}",
        annotation_position="top right",
    )
    fig.update_xaxes(type="log", title_text="Ridge alpha (log scale)")
    fig.update_yaxes(title_text="CV RMSE (minutes)")
    fig.update_layout(
        height=500,
        title_text="Ridge Alpha Sweep - Cross-Validated RMSE",
        margin=dict(l=75, r=35, t=80, b=70),
        template="plotly_white",
        font=dict(size=11),
    )
    return plotly_fragment(fig)


def make_model_comparison_plot(compare_df: pd.DataFrame) -> str:
    """Notebook cell 33: model-family CV comparison."""
    if compare_df.empty:
        raise ValueError("Model comparison did not produce any rows.")

    plot_df = compare_df.sort_values("Mean CV RMSE", ascending=False)
    colors = ["#4682b4" if str(name).startswith("Ridge") else "#d1d5db" for name in plot_df["Model"]]

    fig = go.Figure(
        go.Bar(
            x=plot_df["Mean CV RMSE"],
            y=plot_df["Model"],
            orientation="h",
            error_x=dict(type="data", array=plot_df["Std  CV RMSE"], visible=True),
            marker_color=colors,
        )
    )
    fig.update_xaxes(title_text="Mean Cross-Validated RMSE (minutes)")
    fig.update_yaxes(title_text="Model")
    fig.update_layout(
        height=500,
        title_text="Model Comparison - 5-Fold CV",
        margin=dict(l=165, r=35, t=80, b=70),
        template="plotly_white",
        font=dict(size=11),
    )
    return plotly_fragment(fig)


def make_stage_diagnosis_dashboard(events: pd.DataFrame, daily: pd.DataFrame, outcome: pd.DataFrame) -> str:
    """Notebook cell 48: four-panel stage diagnosis dashboard."""
    tuckman_scores = score_tuckman_stages(events, daily, outcome)
    tribal_scores = score_tribal_stages(events)

    tuckman_stage = max(tuckman_scores, key=tuckman_scores.get)
    tribal_stage = max(tribal_scores, key=tribal_scores.get)

    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Tuckman Group Development",
            "Tribal Leadership Stages",
            "Diagnosed Stage Tracks",
            "Diagnosis Summary",
        ),
        specs=[[{}, {}], [{"type": "scatter"}, {"type": "scatter"}]],
        horizontal_spacing=0.18,
        vertical_spacing=0.18,
    )

    t_order = ["Forming", "Storming", "Norming", "Performing", "Adjourning"]
    t_values = [tuckman_scores.get(s, 0) for s in t_order]
    t_colors = ["#d97706" if s == tuckman_stage else "#94a3b8" for s in t_order]
    fig.add_trace(
        go.Bar(
            y=t_order,
            x=t_values,
            orientation="h",
            marker_color=t_colors,
            text=[f"{v:.2f}" for v in t_values],
            textposition="outside",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    tr_order = [
        "1 — Despairing Hostility",
        "2 — Apathetic Victim",
        "3 — Lone Warrior",
        "4 — Tribal Pride",
        "5 — Innocent Wonderment",
    ]
    tr_display = ["1 Hostility", "2 Victim", "3 Lone Warrior", "4 Pride", "5 Wonderment"]
    tr_values = [tribal_scores.get(s, 0) for s in tr_order]
    tr_colors = ["#7c3aed" if s == tribal_stage else "#94a3b8" for s in tr_order]
    fig.add_trace(
        go.Bar(
            y=tr_display,
            x=tr_values,
            orientation="h",
            marker_color=tr_colors,
            text=[f"{v:.2f}" for v in tr_values],
            textposition="outside",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    track_x = np.arange(1, 6)
    tribal_short = ["1 Hostility", "2 Victim", "3 Lone", "4 Pride", "5 Wonder"]
    fig.add_trace(
        go.Scatter(
            x=track_x,
            y=[1.35] * 5,
            mode="markers+text",
            marker=dict(size=56, color=["#d97706" if s == tuckman_stage else "#e2e8f0" for s in t_order]),
            text=t_order,
            textposition="middle center",
            textfont=dict(size=9, color=["white" if s == tuckman_stage else "#475569" for s in t_order]),
            hovertext=[f"{s}: {tuckman_scores[s]:.2f}" for s in t_order],
            hoverinfo="text",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=track_x,
            y=[0.35] * 5,
            mode="markers+text",
            marker=dict(size=56, color=["#7c3aed" if s == tribal_stage else "#e2e8f0" for s in tr_order]),
            text=tribal_short,
            textposition="middle center",
            textfont=dict(size=9, color=["white" if s == tribal_stage else "#475569" for s in tr_order]),
            hovertext=[f"{label}: {tribal_scores[stage]:.2f}" for label, stage in zip(tr_display, tr_order)],
            hoverinfo="text",
            showlegend=False,
        ),
        row=2,
        col=1,
    )
    fig.add_annotation(text="<b>Tuckman Stage</b>", x=3, y=1.85, showarrow=False, row=2, col=1)
    fig.add_annotation(text="<b>Tribal Stage</b>", x=3, y=0.85, showarrow=False, row=2, col=1)

    metric_lines = [
        "<b>DIAGNOSIS SUMMARY</b>",
        "",
        f"<b>Group Development:</b> {tuckman_stage}",
        f"Confidence: {tuckman_scores[tuckman_stage]:.2f}",
        "",
        f"<b>Tribal Culture:</b> {tribal_stage}",
        f"Confidence: {tribal_scores[tribal_stage]:.2f}",
        "",
        f"Total events: {len(events)}",
        f"Unique actors: {events['actor'].nunique()}",
        f"Date range: {events['date'].min().date()} to {events['date'].max().date()}",
        f"Avg daily EU: {daily['total_eu'].mean():.1f}",
        f"Median response: {outcome['median_response_min'].median():.1f} min" if len(outcome) else "Median response: n/a",
    ]
    fig.add_trace(
        go.Scatter(
            x=[0.03],
            y=[0.92],
            mode="text",
            text=["<br>".join(metric_lines)],
            textposition="top left",
            textfont=dict(size=12, color="#0f172a", family="monospace"),
            hoverinfo="skip",
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    fig.update_xaxes(title_text="Score", range=[0, 1.15], row=1, col=1)
    fig.update_xaxes(title_text="Score", range=[0, 1.15], row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=2)
    fig.update_xaxes(range=[0.5, 5.5], showticklabels=False, zeroline=False, row=2, col=1)
    fig.update_yaxes(range=[0, 2.1], showticklabels=False, zeroline=False, row=2, col=1)
    fig.update_xaxes(range=[0, 1], showticklabels=False, zeroline=False, row=2, col=2)
    fig.update_yaxes(range=[0, 1], showticklabels=False, zeroline=False, row=2, col=2)

    fig.update_layout(
        height=850,
        showlegend=False,
        title_text="OTQ Stage-Diagnosis Dashboard",
        margin=dict(l=105, r=35, t=95, b=70),
        template="plotly_white",
        font=dict(size=11),
    )
    fig.update_annotations(font_size=12)
    return plotly_fragment(fig)


def make_model_diagnostics(model_df: pd.DataFrame, model: Any, model_info: Optional[Dict[str, Any]] = None) -> str:
    """Generate 2x2 model diagnostics as Plotly subplots."""
    from plotly.subplots import make_subplots
    
    X = model_df[["log_total_eu", "log_total_events", "avg_participants", "avg_duration", "log_total_text"]].fillna(0.0)
    y_true = model_df["median_response_min"]
    y_pred = model.predict(X.to_numpy())
    y_test = model_info.get("y_test") if model_info else None
    pred_test = model_info.get("pred_test") if model_info else None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Actual vs Predicted (Test Set)", "Trend Over Time",
                       "EU vs Response Time", "Residual Plot"),
        specs=[[{}, {}], [{}, {}]],
        horizontal_spacing=0.16,
        vertical_spacing=0.18
    )
    
    # Plot 1: Actual vs Predicted scatter
    actual_scatter = y_test if y_test is not None else y_true
    predicted_scatter = pred_test if pred_test is not None else y_pred
    fig.add_trace(go.Scatter(x=actual_scatter, y=predicted_scatter, mode="markers", name="Predictions",
                            marker=dict(color="#3366ff")),
                  row=1, col=1)
    lims = [min(np.min(actual_scatter), np.min(predicted_scatter)), max(np.max(actual_scatter), np.max(predicted_scatter))]
    fig.add_trace(go.Scatter(x=lims, y=lims, mode="lines", name="Perfect fit",
                            line=dict(color="red", dash="dash")),
                  row=1, col=1)
    
    # Plot 2: Trend over time
    model_df_sorted = model_df.sort_values("date")
    fig.add_trace(go.Scatter(x=model_df_sorted["date"], y=model_df_sorted["median_response_min"],
                            mode="lines", name="Actual", line=dict(color="#3366ff")),
                  row=1, col=2)
    fig.add_trace(go.Scatter(x=model_df_sorted["date"], y=y_pred,
                            mode="lines", name="Predicted", line=dict(color="#ff7f0e", dash="dash")),
                  row=1, col=2)
    
    # Plot 3: EU vs Response Time
    fig.add_trace(go.Scatter(x=model_df["total_eu"], y=y_true, mode="markers",
                            name="EU vs Response", marker=dict(color="#51cf66")),
                  row=2, col=1)
    
    # Plot 4: Residual plot
    residuals = y_true - y_pred
    fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode="markers",
                            marker=dict(color="#9b59b6")),
                  row=2, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=2)
    
    fig.update_xaxes(title_text="Actual (min)", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_xaxes(title_text="Total EU", row=2, col=1)
    fig.update_xaxes(title_text="Predicted Value", row=2, col=2)
    
    fig.update_yaxes(title_text="Predicted (min)", row=1, col=1)
    fig.update_yaxes(title_text="Response (min)", row=1, col=2)
    fig.update_yaxes(title_text="Response (min)", row=2, col=1)
    fig.update_yaxes(title_text="Residual", row=2, col=2)
    
    fig.update_layout(
        height=760,
        showlegend=True,
        title_text="Model Diagnostics",
        margin=dict(l=75, r=35, t=95, b=75),
        template="plotly_white",
        font=dict(size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_annotations(font_size=12)
    return plotly_fragment(fig)


def make_model_diagnostics_png(model_df: pd.DataFrame, model: Any, model_info: Dict[str, Any]) -> str:
    """Notebook cell 39: model diagnostics rendered as a PNG."""
    feature_cols = model_info["feature_columns"]
    target_col = "median_response_min"

    model_df_plot = model_df.sort_values("date").copy()
    model_df_plot["pred"] = model.predict(model_df_plot[feature_cols].fillna(0.0).to_numpy())
    model_df_plot["residual"] = model_df_plot[target_col] - model_df_plot["pred"]

    y_test = model_info.get("y_test")
    pred_test = model_info.get("pred_test")
    if y_test is None or pred_test is None:
        y_test = model_df_plot[target_col].to_numpy()
        pred_test = model_df_plot["pred"].to_numpy()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("OTQ Model Diagnostics & Visualizations", fontsize=14, fontweight="bold")

    axes[0, 0].scatter(y_test, pred_test, alpha=0.7, color="steelblue", edgecolors="white")
    lims = [min(np.min(y_test), np.min(pred_test)), max(np.max(y_test), np.max(pred_test))]
    axes[0, 0].plot(lims, lims, "r--", linewidth=1, label="Perfect fit")
    axes[0, 0].set_xlabel("Actual Median Response (min)")
    axes[0, 0].set_ylabel("Predicted Median Response (min)")
    axes[0, 0].set_title("Actual vs Predicted (Test Set)")
    axes[0, 0].legend()

    axes[0, 1].plot(model_df_plot["date"], model_df_plot[target_col], label="Actual", linewidth=1.5, color="steelblue")
    axes[0, 1].plot(model_df_plot["date"], model_df_plot["pred"], label="Predicted", linewidth=1.5, color="coral", linestyle="--")
    axes[0, 1].set_xlabel("Date")
    axes[0, 1].set_ylabel("Median Response (min)")
    axes[0, 1].set_title("Response Time Trend: Actual vs Predicted")
    axes[0, 1].legend()
    axes[0, 1].tick_params(axis="x", rotation=30)

    axes[1, 0].scatter(
        model_df_plot["total_eu"],
        model_df_plot[target_col],
        alpha=0.6,
        color="mediumseagreen",
        edgecolors="white",
    )
    axes[1, 0].set_xlabel("Total Daily EU (Engagement Score)")
    axes[1, 0].set_ylabel("Median Response Time (min)")
    axes[1, 0].set_title("Engagement (EU) vs Response Time\n(Core OTQ Relationship)")

    axes[1, 1].scatter(
        model_df_plot["pred"],
        model_df_plot["residual"],
        alpha=0.6,
        color="slateblue",
        edgecolors="white",
    )
    axes[1, 1].axhline(0, color="red", linestyle="--", linewidth=1)
    axes[1, 1].set_xlabel("Predicted Value")
    axes[1, 1].set_ylabel("Residual (Actual - Predicted)")
    axes[1, 1].set_title("Residual Plot\n(Random scatter = good fit)")

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def make_coefficient_plot(model_info: Dict[str, Any]) -> str:
    """Notebook cell 40: signed Ridge coefficient chart."""
    coefs_df = pd.DataFrame(model_info["coefficients"]).rename(
        columns={"feature": "Feature", "coefficient": "Coefficient"}
    )
    coefs_df = coefs_df.sort_values("Coefficient", ascending=True)
    colors = ["#ff7f50" if value < 0 else "#4682b4" for value in coefs_df["Coefficient"]]

    fig = go.Figure(
        go.Bar(
            x=coefs_df["Coefficient"],
            y=coefs_df["Feature"],
            orientation="h",
            marker_color=colors,
            showlegend=False,
        )
    )
    fig.add_vline(x=0, line_color="#111827", line_width=1)
    fig.update_xaxes(title_text="Coefficient Value")
    fig.update_yaxes(title_text="Feature")
    fig.update_layout(
        height=470,
        title_text="Ridge Regression Coefficients",
        margin=dict(l=145, r=35, t=80, b=65),
        template="plotly_white",
        font=dict(size=11),
    )
    return plotly_fragment(fig)


def make_permutation_importance_plot(model: Any, model_info: Dict[str, Any], X_test: np.ndarray, y_test: np.ndarray) -> str:
    """Notebook cell 42: permutation importance on the held-out test set."""
    feature_cols = model_info["feature_columns"]
    n_repeats = 30 if len(y_test) >= 4 else 10
    perm = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=n_repeats,
        random_state=42,
        scoring="neg_mean_squared_error",
    )
    perm_df = pd.DataFrame(
        {
            "Feature": feature_cols,
            "Mean Importance": perm.importances_mean,
            "Std Importance": perm.importances_std,
        }
    ).sort_values("Mean Importance", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=perm_df["Mean Importance"],
            y=perm_df["Feature"],
            orientation="h",
            error_x=dict(type="data", array=perm_df["Std Importance"], visible=True),
            marker_color="#6a5acd",
            showlegend=False,
        )
    )
    fig.update_xaxes(title_text="Increase in MSE when feature is shuffled")
    fig.update_yaxes(title_text="Feature")
    fig.update_layout(
        height=500,
        title_text="Permutation Feature Importance - Ridge",
        margin=dict(l=145, r=35, t=80, b=75),
        template="plotly_white",
        font=dict(size=11),
    )
    return plotly_fragment(fig)


def make_feature_importance(model_info: Dict[str, Any], model_df: pd.DataFrame, model: Any) -> str:
    """Generate feature importance as two side-by-side Plotly bar charts."""
    from plotly.subplots import make_subplots
    
    # Coefficients
    coefs_df = pd.DataFrame(model_info["coefficients"]).sort_values("coefficient")
    coef_colors = ["#ff6b6b" if x < 0 else "#3366ff" for x in coefs_df["coefficient"]]
    
    # Permutation importance
    X = model_df[["log_total_eu", "log_total_events", "avg_participants", "avg_duration", "log_total_text"]].fillna(0.0)
    y = model_df["median_response_min"]
    
    try:
        perm = permutation_importance(model, X.to_numpy(), y, n_repeats=10, random_state=42, n_jobs=-1)
        perm_df = pd.DataFrame({
            "feature": X.columns,
            "importance": perm.importances_mean
        }).sort_values("importance", ascending=True)
    except:
        perm_df = pd.DataFrame({"feature": [], "importance": []})
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Ridge Coefficients", "Permutation Importance"),
        specs=[[{}, {}]],
        horizontal_spacing=0.18
    )
    
    fig.add_trace(go.Bar(x=coefs_df["coefficient"], y=coefs_df["feature"],
                        orientation="h", marker_color=coef_colors, showlegend=False),
                  row=1, col=1)
    
    if not perm_df.empty:
        fig.add_trace(go.Bar(x=perm_df["importance"], y=perm_df["feature"],
                            orientation="h", marker_color="#7c3aed", showlegend=False),
                      row=1, col=2)
    
    fig.update_xaxes(title_text="Coefficient", row=1, col=1)
    fig.update_xaxes(title_text="Importance", row=1, col=2)
    
    fig.update_layout(
        height=460,
        showlegend=False,
        title_text="Feature Importance Analysis",
        margin=dict(l=135, r=35, t=85, b=65),
        template="plotly_white",
        font=dict(size=11),
    )
    fig.update_annotations(font_size=12)
    return plotly_fragment(fig)


def make_data_summary(events: pd.DataFrame, file_counts: Dict[str, int]) -> Dict[str, Any]:
    """Generate data summary tables for display."""
    source_counts = {}
    for source in ["slack", "teams", "outlook"]:
        source_events = events[events["source"] == source]
        if len(source_events) > 0:
            source_counts[source.upper()] = len(source_events)
    
    # Sample data (first 3 rows from each source)
    samples = {}
    for source in ["slack", "teams", "outlook"]:
        source_df = events[events["source"] == source]
        if len(source_df) > 0:
            samples[source] = source_df.head(3)[["source", "event_type", "timestamp", "actor", "channel"]].to_dict("records")
    
    return {
        "file_counts": file_counts,
        "source_counts": source_counts,
        "samples": samples,
        "total_events": len(events),
        "unique_actors": events["actor"].nunique(),
    }


try:
    from textblob import TextBlob
    _HAS_TEXTBLOB = True
except Exception:
    _HAS_TEXTBLOB = False


def cv_rmse(estimator, X, y, n_splits=5, random_state=42):
    n_splits = min(n_splits, len(y))
    if n_splits < 2:
        return np.array([np.nan])
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    neg_mse = cross_val_score(estimator, X, y, scoring="neg_mean_squared_error", cv=kf)
    return np.sqrt(-neg_mse)


def cv_r2(estimator, X, y, n_splits=5, random_state=42):
    n_splits = min(n_splits, len(y))
    if n_splits < 2:
        return np.array([np.nan])
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    return cross_val_score(estimator, X, y, scoring="r2", cv=kf)


def alpha_sweep(X, y, alphas=None):
    if alphas is None:
        alphas = np.logspace(-3, 3, 13)
    mean_rmse = np.zeros(len(alphas))
    std_rmse = np.zeros(len(alphas))
    for i, a in enumerate(alphas):
        folds = cv_rmse(Ridge(alpha=a), X, y)
        mean_rmse[i] = folds.mean()
        std_rmse[i] = folds.std()
    best_idx = int(np.argmin(mean_rmse))
    best_alpha = float(alphas[best_idx])
    alpha_table = pd.DataFrame({
        "alpha": np.round(alphas, 4),
        "Mean CV RMSE": np.round(mean_rmse, 3),
        "Std  CV RMSE": np.round(std_rmse, 3),
    })
    return best_alpha, alpha_table


def tune_ridge_via_grid(X, y):
    param_grid = {
        "alpha": np.logspace(-3, 3, 13),
        "solver": ["auto", "cholesky", "lsqr"],
    }
    grid = GridSearchCV(
        estimator=Ridge(),
        param_grid=param_grid,
        scoring="neg_mean_squared_error",
        cv=KFold(n_splits=5, shuffle=True, random_state=42),
        n_jobs=-1,
        verbose=0,
    )
    grid.fit(X, y)
    tuned_rmse = float(np.sqrt(-grid.best_score_))
    return grid.best_estimator_, grid.best_params_, tuned_rmse


def compare_model_families(X, y, best_alpha=None):
    if best_alpha is None:
        best_alpha = 1.0
    candidates = {
        "Ridge (best alpha)": Ridge(alpha=best_alpha),
        "Lasso": Lasso(alpha=0.1, max_iter=10_000),
        "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10_000),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42),
    }
    rows = []
    for name, est in candidates.items():
        folds_rmse = cv_rmse(est, X, y)
        folds_r2 = cv_r2(est, X, y)
        rows.append({
            "Model": name,
            "Mean CV RMSE": round(float(folds_rmse.mean()), 3),
            "Std  CV RMSE": round(float(folds_rmse.std()), 3),
            "Mean CV R^2": round(float(folds_r2.mean()), 3),
            "Std  CV R^2": round(float(folds_r2.std()), 3),
        })
    compare_df = pd.DataFrame(rows).sort_values("Mean CV RMSE").reset_index(drop=True)
    return compare_df


# ── Optional sentiment enrichment (gated) ─────────────────────────────────────
ENABLE_SENTIMENT_DEMO = False


TRIBAL_LEXICONS = {
    "1_despairing_hostility": [
        "hate", "stupid", "useless", "broken", "rage", "furious",
        "terrible", "awful", "worst", "disaster", "blame", "fault",
        "incompetent", "lying", "betrayed", "enemy", "fight", "war",
    ],
    "2_apathetic_victim": [
        "can't", "cant", "won't", "wont", "stuck", "tired", "exhausted",
        "always", "never", "again", "whatever", "nothing matters",
        "give up", "pointless", "hopeless", "overwhelmed", "complain",
        "unfair", "they make us",
    ],
    "3_lone_warrior": [
        " i ", "i'll", "ill ", "i'm", "im ", "myself", "my ",
        "alone", "myself", "i did", "i will", "i can",
        "without them", "on my own",
    ],
    "4_tribal_pride": [
        "we ", "us ", "our ", "team", "together", "collaborate",
        "partner", "group", "joint", "with you", "with the team",
        "we are", "we will", "we did", "let us", "let's",
    ],
    "5_innocent_wonderment": [
        "vision", "mission", "purpose", "world", "transform",
        "inspire", "everyone", "humanity", "future", "legacy",
        "amazing", "wonder", "marvelous", "beauty", "love",
        "joy", "peace", "spirit", "gospel", "grace", "faith", "hope",
    ],
}


def _score_text_against_lexicon(text_blob: str, lexicon: list) -> float:
    if not text_blob:
        return 0.0
    text_blob = " " + text_blob.lower() + " "
    hits = sum(text_blob.count(k.lower()) for k in lexicon)
    return hits / max(len(text_blob.split()) / 50, 1.0)


def score_tuckman_stages(events_df, daily_df, outcome_df):
    if len(events_df) == 0 or len(daily_df) == 0:
        return {s: 0.0 for s in ["Forming", "Storming", "Norming", "Performing", "Adjourning"]}

    total_eu = daily_df["total_eu"].sum()
    avg_daily_eu = daily_df["total_eu"].mean()
    eu_volatility = daily_df["total_eu"].std() / max(avg_daily_eu, 1e-6)
    unique_actors = events_df["actor"].nunique()
    total_events = len(events_df)

    actor_counts = events_df["actor"].value_counts().to_numpy().astype(float)
    if len(actor_counts) > 1:
        sorted_counts = np.sort(actor_counts)
        cum = np.cumsum(sorted_counts)
        gini = (2 * np.sum((np.arange(1, len(sorted_counts) + 1)) * sorted_counts) / (len(sorted_counts) * cum[-1])) - (len(sorted_counts) + 1) / len(sorted_counts)
        gini = float(np.clip(gini, 0, 1))
    else:
        gini = 1.0

    if len(daily_df) >= 4:
        days_idx = np.arange(len(daily_df))
        slope = np.polyfit(days_idx, daily_df["total_eu"].to_numpy(), 1)[0]
        trend = slope / max(avg_daily_eu, 1e-6)
        half = len(daily_df) // 2
        recent_avg = daily_df["total_eu"].iloc[half:].mean()
        early_avg = daily_df["total_eu"].iloc[:half].mean()
        recent_lift = (recent_avg - early_avg) / max(early_avg, 1e-6)
    else:
        trend = 0.0
        recent_lift = 0.0

    if len(outcome_df) > 0:
        rt_mean = float(outcome_df["median_response_min"].mean())
        rt_var = float(outcome_df["median_response_min"].std() / max(outcome_df["median_response_min"].mean(), 1e-6))
    else:
        rt_mean, rt_var = 60.0, 1.0

    n_eu_vol = float(np.clip(eu_volatility, 0, 1.5)) / 1.5
    n_low_volume = 1.0 - float(np.clip(total_events / 80.0, 0, 1.0))
    n_high_volume = float(np.clip(total_events / 80.0, 0, 1.0))
    n_narrow = 1.0 - float(np.clip(unique_actors / 12.0, 0, 1.0))
    n_broad = float(np.clip(unique_actors / 12.0, 0, 1.0))
    n_balanced = 1.0 - gini
    n_concentrated = gini
    n_pos_trend = float(np.clip(trend + 0.5, 0, 1.0))
    n_neg_trend = float(np.clip(-trend + 0.5, 0, 1.0))
    n_recent_lift = float(np.clip(recent_lift + 0.5, 0, 1.0))
    n_recent_drop = float(np.clip(-recent_lift + 0.5, 0, 1.0))
    n_fast_rt = 1.0 - float(np.clip(rt_mean / 240.0, 0, 1.0))
    n_high_rt_var = float(np.clip(rt_var, 0, 1.5)) / 1.5
    n_low_rt_var = 1.0 - n_high_rt_var

    scores = {
        "Forming": 0.35 * n_low_volume + 0.25 * n_narrow + 0.20 * n_high_rt_var + 0.20 * n_eu_vol,
        "Storming": 0.35 * n_eu_vol + 0.30 * n_concentrated + 0.20 * n_high_rt_var + 0.15 * n_low_rt_var * 0,
        "Norming": 0.30 * n_pos_trend + 0.30 * n_balanced + 0.25 * n_recent_lift + 0.15 * n_fast_rt,
        "Performing": 0.30 * n_high_volume + 0.25 * n_broad + 0.25 * n_fast_rt + 0.20 * n_low_rt_var,
        "Adjourning": 0.45 * n_neg_trend + 0.35 * n_recent_drop + 0.20 * n_low_volume,
    }
    return {k: float(np.clip(v, 0, 1)) for k, v in scores.items()}


def score_tribal_stages(events_df):
    stage_labels = {
        "1_despairing_hostility": "1 — Despairing Hostility",
        "2_apathetic_victim": "2 — Apathetic Victim",
        "3_lone_warrior": "3 — Lone Warrior",
        "4_tribal_pride": "4 — Tribal Pride",
        "5_innocent_wonderment": "5 — Innocent Wonderment",
    }
    if len(events_df) == 0:
        return {v: 0.0 for v in stage_labels.values()}
    text_blob = " ".join(events_df["text"].dropna().astype(str).tolist()).strip()
    unique_actors = events_df["actor"].nunique()
    avg_participants = float(events_df["participant_count"].clip(lower=1).mean())
    has_meetings = (events_df["event_type"].str.contains("meeting", case=False, na=False)).sum()
    meeting_share = has_meetings / max(len(events_df), 1)
    network_breadth = unique_actors / 13.0
    network_breadth = float(np.clip(network_breadth, 0, 1))
    raw = {key: _score_text_against_lexicon(text_blob, lex) for key, lex in TRIBAL_LEXICONS.items()}
    raw["1_despairing_hostility"] *= (0.8 + 0.4 * (1 - network_breadth))
    raw["2_apathetic_victim"] *= (0.8 + 0.4 * (1 - network_breadth))
    raw["3_lone_warrior"] *= (0.7 + 0.6 * (1 - meeting_share))
    raw["4_tribal_pride"] *= (0.7 + 0.6 * meeting_share + 0.3 * network_breadth)
    raw["5_innocent_wonderment"] *= (0.6 + 0.4 * network_breadth + 0.2 * (avg_participants / 10))
    peak = max(raw.values()) or 1.0
    return {stage_labels[k]: float(np.clip(v / peak, 0, 1)) for k, v in raw.items()}

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

    # Generate all plots for frontend display
    plots = []
    data_summary = make_data_summary(events, file_counts)
    
    try:
         # --- Original Matplotlib PNG plots (kept for reference, commented out) ---
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

        # # Plot 1: EU distribution (Plotly)
        # eu_vals = events["eu"].dropna()
        # if eu_vals.nunique() <= 1:
        #     val = float(eu_vals.iloc[0]) if len(eu_vals) > 0 else 0.0
        #     fig_px = px.bar(x=[val], y=[len(eu_vals)], labels={"x": "EU", "y": "count"},
        #                     title="Event Units (EU) Distribution (single value)", template="plotly_white")
        # else:
        #     fig_px = px.histogram(events, x="eu", nbins=30, title="Event Units (EU) Distribution",
        #                           labels={"eu": "EU"}, template="plotly_white")
        # fig_px.update_layout(height=350)
        # html1 = pio.to_html(fig_px, include_plotlyjs=False, full_html=False)
        # plots.append({"title": "EU Distribution", "type": "plotly", "html": html1})

        # # Plot 2: Feature Coefficients (Plotly)
        # coefs_df = pd.DataFrame(model_info["coefficients"]).sort_values(by="coefficient")
        # fig_coefs = go.Figure(go.Bar(x=coefs_df['coefficient'], y=coefs_df['feature'], orientation='h', marker_color='#2b8aef'))
        # fig_coefs.update_layout(title_text='Feature Coefficients (sorted)', template='plotly_white', height=350)
        # html2 = pio.to_html(fig_coefs, include_plotlyjs=False, full_html=False)
        # plots.append({"title": "Feature Coefficients", "type": "plotly", "html": html2})

        # # Plot 3: Actual vs Predicted over time (Plotly)
        # fig_trend = go.Figure()
        # fig_trend.add_trace(go.Scatter(x=model_df['date'], y=model_df['median_response_min'], mode='lines+markers', name='Actual', line=dict(color='#3366ff')))
        # fig_trend.add_trace(go.Scatter(x=model_df['date'], y=model_df['predicted_response_min'], mode='lines+markers', name='Predicted', line=dict(color='#ff7f0e')))
        # fig_trend.update_layout(title='Actual vs Predicted Median Response (by date)', xaxis_title='Date', yaxis_title='Median response (minutes)', template='plotly_white', height=350)
        # html3 = pio.to_html(fig_trend, include_plotlyjs=False, full_html=False)
        # plots.append({"title": "Actual vs Predicted", "type": "plotly", "html": html3})

    except Exception as e:
        plots.append({"title": "plots_error", "data": str(e)})

    def add_plot(title: str, make_html: Any) -> None:
        try:
            plots.append({"title": title, "type": "plotly", "html": make_html()})
        except Exception as exc:
            plots.append({"title": "plots_error", "data": f"{title}: {exc}"})

    def add_png_plot(title: str, make_png: Any) -> None:
        try:
            plots.append({"title": title, "data": make_png()})
        except Exception as exc:
            plots.append({"title": "plots_error", "data": f"{title}: {exc}"})

    X_all = model_df[feature_cols].fillna(0.0).to_numpy()
    y_all = model_df["median_response_min"].fillna(model_df["median_response_min"].median()).to_numpy()

    add_png_plot("Exploratory Data Analysis", lambda: make_eda_plots_png(events, daily, outcome))
    add_png_plot("Correlation Heatmap", lambda: make_correlation_heatmap_png(daily))
    add_plot("Source and Channel Breakdown", lambda: make_source_channel_breakdown(events))
    add_plot("Ridge Alpha Sweep", lambda: make_alpha_sweep_plot(X_all, y_all))
    add_png_plot("Model Diagnostics", lambda: make_model_diagnostics_png(model_df, model, model_info))
    add_plot("Ridge Coefficients", lambda: make_coefficient_plot(model_info))
    add_plot("Permutation Importance", lambda: make_permutation_importance_plot(model, model_info, model_info["X_test"], model_info["y_test"]))
    add_plot("Stage Diagnosis Dashboard", lambda: make_stage_diagnosis_dashboard(events, daily, outcome))

    return {
        "pipeline_build": PIPELINE_BUILD,
        "file_counts": file_counts,
        "data_summary": data_summary,
        "event_rows": int(events.shape[0]),
        "daily_rows": int(daily.shape[0]),
        "outcome_rows": int(outcome.shape[0]),
        "model_rows": int(model_df.shape[0]),
        "metrics": model_info["metrics"],
        "coefficients": model_info["coefficients"],
        "recent_predictions": recent_predictions,
        "plots": plots,
    }
