"""
Trading Journal v3 - Professional Trading Software
Features:
- Login / Register / Forgot Password / Remember Me
- Multiple Trading Accounts per user
- Trade Entry (Buy/Sell, Screenshot, Mood, Notes)
- Trade Edit + Delete with Confirmation
- Trade Detail Popup
- Dashboard: Equity Curve, Win Rate, PnL, Profit Factor, Max Drawdown
- Monthly Calendar PnL View
- Day-of-Week Analysis
- Drawdown Chart
- Risk Management: Daily Loss Limit + Position Size Calculator
- Mood Tracker (per trade psychology)
- Weekly Review Journal
- Leaderboard
- Admin Panel
- Dark/Light Theme Toggle
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import hashlib, secrets as _secrets
from datetime import datetime, date, timedelta
import calendar
import streamlit.components.v1 as components
from supabase import create_client, Client

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Trading Journal", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

ADMIN_USERNAME = "LIONLUCKY11"

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
def apply_theme():
    dark = st.session_state.get("dark_mode", True)
    if dark:
        bg       = "#0a0e17"
        bg2      = "#111827"
        bg3      = "#1a2235"
        bg4      = "#243049"
        text     = "#f1f5f9"
        muted    = "#94a3b8"
        border   = "#2d3748"
        accent   = "#3b82f6"
        accent2  = "#60a5fa"
        green    = "#22c55e"
        red      = "#ef4444"
        gold     = "#f59e0b"
    else:
        bg       = "#f8fafc"
        bg2      = "#ffffff"
        bg3      = "#f1f5f9"
        bg4      = "#e2e8f0"
        text     = "#0f172a"
        muted    = "#64748b"
        border   = "#e2e8f0"
        accent   = "#2563eb"
        accent2  = "#3b82f6"
        green    = "#16a34a"
        red      = "#dc2626"
        gold     = "#d97706"

    st.markdown(f"""<style>
    /* ── Base ── */
    .stApp {{ background-color:{bg}; color:{text}; font-family:'Inter',sans-serif; }}
    .main .block-container {{ padding:1rem 1.5rem 2rem; max-width:1400px; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background:linear-gradient(180deg,{bg2} 0%,{bg3} 100%);
        border-right:1px solid {border};
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background:{bg4}; color:{text}; border:1px solid {border};
        border-radius:8px; font-weight:500; margin-bottom:4px;
        transition:all 0.2s;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background:{accent}; color:white; border-color:{accent};
        transform:translateX(4px);
    }}

    /* ── Metrics ── */
    [data-testid="metric-container"] {{
        background:linear-gradient(135deg,{bg2},{bg3});
        border:1px solid {border}; border-radius:12px;
        padding:1rem; transition:transform 0.2s;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    }}
    [data-testid="metric-container"]:hover {{ transform:translateY(-2px); }}
    [data-testid="metric-container"] label {{ color:{muted} !important; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color:{accent2}; font-size:1.6rem; font-weight:800; letter-spacing:-0.02em;
    }}
    [data-testid="stMetricDelta"] svg {{ display:none; }}

    /* ── Inputs ── */
    .stTextInput input, .stNumberInput input, .stDateInput input {{
        background:{bg3} !important; color:{text} !important;
        border:1px solid {border} !important; border-radius:8px !important;
        padding:0.5rem 0.75rem !important; font-size:0.9rem !important;
        transition:border-color 0.2s !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color:{accent} !important;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15) !important;
    }}
    .stTextArea textarea {{
        background:{bg3} !important; color:{text} !important;
        border:1px solid {border} !important; border-radius:8px !important;
        font-family:'JetBrains Mono','Fira Code',monospace !important;
        font-size:0.88rem !important; line-height:1.6 !important;
    }}
    .stTextArea textarea:focus {{
        border-color:{accent} !important;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15) !important;
    }}
    .stSelectbox > div > div {{
        background:{bg3} !important; border-color:{border} !important;
        border-radius:8px !important; color:{text} !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background:linear-gradient(135deg,{accent},{accent2});
        color:white; border:none; border-radius:8px;
        font-weight:600; font-size:0.88rem; letter-spacing:0.02em;
        padding:0.5rem 1rem; transition:all 0.2s;
        box-shadow:0 2px 6px rgba(59,130,246,0.3);
    }}
    .stButton > button:hover {{
        transform:translateY(-2px);
        box-shadow:0 6px 16px rgba(59,130,246,0.4);
        filter:brightness(1.08);
    }}
    .stButton > button:active {{ transform:translateY(0); }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background:{bg2}; border-bottom:2px solid {border};
        gap:4px; padding:0 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color:{muted}; padding:0.6rem 1.2rem; border-radius:8px 8px 0 0;
        font-weight:500; font-size:0.88rem; transition:all 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color:{text}; background:{bg3}; }}
    .stTabs [aria-selected="true"] {{
        background:{bg3} !important; color:{accent} !important;
        border-bottom:3px solid {accent} !important; font-weight:700;
    }}

    /* ── Dataframe ── */
    .stDataFrame {{ background:{bg2}; border:1px solid {border}; border-radius:12px; overflow:hidden; }}
    .stDataFrame thead {{ background:{bg3}; }}

    /* ── Cards ── */
    .insight-card {{
        background:linear-gradient(135deg,{bg2},{bg3});
        border:1px solid {border}; border-left:4px solid {accent};
        border-radius:10px; padding:0.8rem 1.2rem; margin-bottom:0.5rem;
        transition:transform 0.2s;
    }}
    .insight-card:hover {{ transform:translateX(4px); }}
    .notif-card {{
        background:linear-gradient(135deg,{bg2},{bg3});
        border:1px solid {border}; border-left:4px solid {gold};
        border-radius:10px; padding:0.8rem 1.2rem; margin-bottom:0.4rem;
    }}
    .rich-preview {{
        background:{bg3}; border:1px solid {border}; border-radius:8px;
        padding:0.8rem 1rem; margin-top:0.5rem; font-size:0.9rem;
        line-height:1.7; min-height:60px;
    }}

    /* ── Mobile Responsive ── */
    @media (max-width: 768px) {{
        .main .block-container {{ padding:0.5rem 0.8rem; }}
        [data-testid="metric-container"] {{ padding:0.6rem; }}
        [data-testid="metric-container"] [data-testid="stMetricValue"] {{ font-size:1.2rem; }}
        h1 {{ font-size:1.4rem !important; }}
        h2 {{ font-size:1.2rem !important; }}
        h3 {{ font-size:1rem !important; }}
        .stButton > button {{ font-size:0.78rem; padding:0.4rem 0.6rem; }}
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width:4px; height:4px; }}
    ::-webkit-scrollbar-track {{ background:{bg}; }}
    ::-webkit-scrollbar-thumb {{ background:{border}; border-radius:4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background:{muted}; }}

    /* ── Misc ── */
    [data-testid="stFileUploader"] {{
        background:{bg3}; border:2px dashed {border}; border-radius:10px;
        transition:border-color 0.2s;
    }}
    [data-testid="stFileUploader"]:hover {{ border-color:{accent}; }}
    h1,h2,h3,h4 {{ color:{text}; font-weight:700; }}
    hr {{ border-color:{border}; margin:1rem 0; }}
    .stExpander {{ background:{bg2}; border:1px solid {border}; border-radius:10px; }}
    .stCheckbox label {{ color:{text}; }}
    div[data-testid="stProgress"] > div {{ background:{bg3}; border-radius:999px; }}
    div[data-testid="stProgress"] > div > div {{
        background:linear-gradient(90deg,{accent},{green}); border-radius:999px;
    }}
    </style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SUPABASE CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def upload_screenshot(uid, trade_id, img_bytes, filename="screenshot.png"):
    """Upload screenshot to Supabase Storage and return public URL."""
    try:
        sb = get_supabase()
        path = f"{uid}/{trade_id}_{filename}"
        sb.storage.from_("SCREENSHOT").upload(
            path, img_bytes,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        url = sb.storage.from_("SCREENSHOT").get_public_url(path)
        return url
    except Exception as e:
        return None

def delete_screenshot(uid, trade_id):
    """Delete screenshot from Supabase Storage."""
    try:
        sb = get_supabase()
        for ext in ["png","jpg","jpeg","webp"]:
            try:
                sb.storage.from_("SCREENSHOT").remove([f"{uid}/{trade_id}_screenshot.{ext}"])
            except:
                pass
    except:
        pass

def init_db():
    pass  # Tables already created in Supabase SQL Editor

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
def hash_text(t): return hashlib.sha256(t.strip().lower().encode()).hexdigest()

def create_session(uid, uname):
    token = _secrets.token_hex(32)
    sb = get_supabase()
    sb.table("sessions").upsert({"token": token, "user_id": uid, "username": uname}).execute()
    return token

def get_session(token):
    if not token: return None
    sb = get_supabase()
    res = sb.table("sessions").select("user_id,username").eq("token", token).execute()
    if res.data:
        r = res.data[0]
        return (r["user_id"], r["username"])
    return None

def delete_session(token):
    if not token: return
    sb = get_supabase()
    sb.table("sessions").delete().eq("token", token).execute()

def register_user(username, password, sq, sa):
    sb = get_supabase()
    # Check if username exists
    res = sb.table("users").select("id").eq("username", username.strip()).execute()
    if res.data:
        return False, "Username already exists.", None
    res = sb.table("users").insert({
        "username": username.strip(),
        "password_hash": hash_text(password),
        "security_question": sq,
        "security_answer_hash": hash_text(sa)
    }).execute()
    if res.data:
        return True, "Account created!", res.data[0]["id"]
    return False, "Error creating account.", None

def login_user(username, password):
    sb = get_supabase()
    res = sb.table("users").select("id").eq("username", username.strip()).eq("password_hash", hash_text(password)).execute()
    if res.data:
        return res.data[0]["id"]
    return None

def get_security_question(username):
    sb = get_supabase()
    res = sb.table("users").select("id,security_question").eq("username", username.strip()).execute()
    if res.data:
        r = res.data[0]
        return (r["id"], r["security_question"])
    return None

def reset_password(username, answer, new_pw):
    sb = get_supabase()
    res = sb.table("users").select("id").eq("username", username.strip()).eq("security_answer_hash", hash_text(answer)).execute()
    if res.data:
        sb.table("users").update({"password_hash": hash_text(new_pw)}).eq("username", username.strip()).execute()
        return True
    return False

# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────
def get_all_users():
    sb = get_supabase()
    res = sb.table("users").select("id,username,created_at").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def delete_user_completely(uid):
    sb = get_supabase()
    for tbl in ["trades","trading_accounts","sessions"]:
        sb.table(tbl).delete().eq("user_id", uid).execute()
    sb.table("users").delete().eq("id", uid).execute()

# ─────────────────────────────────────────────
# TRADING ACCOUNTS
# ─────────────────────────────────────────────
def create_account(uid, name, broker, size, currency, daily_loss):
    sb = get_supabase()
    res = sb.table("trading_accounts").insert({
        "user_id": uid, "account_name": name, "broker": broker,
        "account_size": size, "currency": currency, "daily_loss_limit": daily_loss
    }).execute()
    return res.data[0]["id"] if res.data else None

def get_accounts(uid):
    sb = get_supabase()
    res = sb.table("trading_accounts").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def delete_account(aid):
    sb = get_supabase()
    sb.table("trades").delete().eq("account_id", aid).execute()
    sb.table("trading_accounts").delete().eq("id", aid).execute()

def get_account_info(aid):
    sb = get_supabase()
    res = sb.table("trading_accounts").select("*").eq("id", aid).execute()
    return res.data[0] if res.data else None

# ─────────────────────────────────────────────
# TRADES
# ─────────────────────────────────────────────
def calc_rr(entry, sl, tp):
    try:
        risk = abs(entry - sl); reward = abs(tp - entry)
        return round(reward/risk, 2) if risk else None
    except: return None

def calc_pnl(result, risk_pct, rr):
    if result == "Win" and rr: return round(risk_pct * rr, 2)
    elif result == "Loss": return round(-risk_pct, 2)
    elif result == "BE": return 0.0
    return None

def save_trade(uid, aid, pair, tdate, session, strategy, direction,
               entry, sl, tp, risk_pct, result, mood, notes, ss=None,
               commission=0.0, swap=0.0, account_size=10000.0):
    rr = calc_rr(entry, sl, tp)
    pnl = calc_pnl(result, risk_pct, rr)
    # Convert $ to % for storage
    comm_pct = round((commission or 0) / account_size * 100, 6) if account_size > 0 else 0
    swap_pct = round((swap or 0) / account_size * 100, 6) if account_size > 0 else 0
    net_pnl = round((pnl or 0) - comm_pct - swap_pct, 4)
    sb = get_supabase()
    # Insert trade first to get ID
    res = sb.table("trades").insert({
        "user_id": uid, "account_id": aid, "pair": pair,
        "trade_date": str(tdate), "session": session, "strategy": strategy,
        "direction": direction, "entry": entry, "stop_loss": sl,
        "take_profit": tp, "risk_pct": risk_pct, "result": result,
        "rr": rr, "pnl": pnl, "net_pnl": net_pnl,
        "commission": commission or 0.0, "swap": swap or 0.0,
        "mood": mood, "notes": notes, "screenshot_url": None
    }).execute()
    # Upload screenshot if provided
    if ss and res.data:
        trade_id = res.data[0]["id"]
        url = upload_screenshot(uid, trade_id, ss, "screenshot.png")
        if url:
            sb.table("trades").update({"screenshot_url": url}).eq("id", trade_id).execute()

def update_trade(tid, pair, tdate, session, strategy, direction,
                 entry, sl, tp, risk_pct, result, mood, notes,
                 commission=0.0, swap=0.0):
    rr = calc_rr(entry, sl, tp)
    pnl = calc_pnl(result, risk_pct, rr)
    net_pnl = round((pnl or 0) - (commission or 0) - (swap or 0), 4)
    sb = get_supabase()
    sb.table("trades").update({
        "pair": pair, "trade_date": str(tdate), "session": session,
        "strategy": strategy, "direction": direction, "entry": entry,
        "stop_loss": sl, "take_profit": tp, "risk_pct": risk_pct,
        "result": result, "rr": rr, "pnl": pnl, "net_pnl": net_pnl,
        "commission": commission or 0.0, "swap": swap or 0.0,
        "mood": mood, "notes": notes
    }).eq("id", tid).execute()

def delete_trade(tid):
    sb = get_supabase()
    sb.table("trades").delete().eq("id", tid).execute()

def load_trades(uid, aid=None):
    sb = get_supabase()
    q = sb.table("trades").select("*").eq("user_id", uid)
    if aid:
        q = q.eq("account_id", aid)
    res = q.order("trade_date", desc=True).execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    if not df.empty:
        df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df

def get_trade_by_id(tid):
    sb = get_supabase()
    res = sb.table("trades").select("*").eq("id", tid).execute()
    return res.data[0] if res.data else None

# ─────────────────────────────────────────────
# GOALS
# ─────────────────────────────────────────────
def save_goal(uid, month, target_pnl, target_trades, target_winrate):
    sb = get_supabase()
    sb.table("goals").delete().eq("user_id", uid).eq("month", month).execute()
    sb.table("goals").insert({
        "user_id": uid, "month": month,
        "target_pnl": target_pnl,
        "target_trades": target_trades,
        "target_winrate": target_winrate
    }).execute()

def get_goal(uid, month):
    sb = get_supabase()
    res = sb.table("goals").select("*").eq("user_id", uid).eq("month", month).execute()
    return res.data[0] if res.data else None

# ─────────────────────────────────────────────
# CHECKLISTS
# ─────────────────────────────────────────────
def save_checklist_template(uid, items):
    sb = get_supabase()
    sb.table("checklists").delete().eq("user_id", uid).execute()
    sb.table("checklists").insert({"user_id": uid, "items": items}).execute()

def get_checklist_template(uid):
    sb = get_supabase()
    res = sb.table("checklists").select("*").eq("user_id", uid).execute()
    return res.data[0]["items"] if res.data else None

# ─────────────────────────────────────────────
# WEEKLY REVIEW
# ─────────────────────────────────────────────
def save_weekly_review(uid, week_start, went_well, improve, lessons, score):
    sb = get_supabase()
    # Delete existing review for this week if any
    sb.table("weekly_reviews").delete().eq("user_id", uid).eq("week_start", str(week_start)).execute()
    sb.table("weekly_reviews").insert({
        "user_id": uid, "week_start": str(week_start),
        "what_went_well": went_well, "what_to_improve": improve,
        "lessons": lessons, "score": score
    }).execute()

def load_weekly_reviews(uid):
    sb = get_supabase()
    res = sb.table("weekly_reviews").select("*").eq("user_id", uid).order("week_start", desc=True).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# ─────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────
def compute_stats(df):
    if df.empty: return {}
    total = len(df)
    wins = (df["result"] == "Win").sum()
    losses = (df["result"] == "Loss").sum()
    win_rate = round(wins/total*100, 1)
    gross_profit = df[df["pnl"] > 0]["pnl"].sum()
    gross_loss = abs(df[df["pnl"] < 0]["pnl"].sum())
    pf = round(gross_profit/gross_loss, 2) if gross_loss else float("inf")
    avg_rr = round(df["rr"].dropna().mean(), 2) if not df["rr"].dropna().empty else 0
    df_s = df.sort_values("trade_date")
    equity = df_s["pnl"].fillna(0).cumsum()
    peak = equity.cummax()
    dd = equity - peak
    max_dd = round(dd.min(), 2)
    return dict(total=total, wins=wins, losses=losses, win_rate=win_rate,
                profit_factor=pf, avg_rr=avg_rr, max_drawdown=max_dd,
                equity=equity, drawdown=dd, dates=df_s["trade_date"])

def equity_chart(dates, equity, drawdown):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=equity, name="Equity",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.08)"))
    fig.add_trace(go.Scatter(x=dates, y=drawdown, name="Drawdown",
        line=dict(color="#f85149", width=1.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(248,81,73,0.06)"))
    fig.update_layout(
        title="Equity & Drawdown Curve",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=40,r=20,t=50,b=40), height=320)
    return fig

def monthly_calendar_chart(df):
    if df.empty: return None
    df_c = df.copy()
    df_c["month"] = df_c["trade_date"].dt.to_period("M")
    monthly = df_c.groupby("month")["pnl"].sum().reset_index()
    monthly["month_str"] = monthly["month"].astype(str)
    monthly["color"] = ["#3fb950" if p >= 0 else "#f85149" for p in monthly["pnl"]]
    fig = go.Figure(go.Bar(
        x=monthly["month_str"], y=monthly["pnl"],
        marker_color=monthly["color"],
        text=[f"{p:+.1f}%" for p in monthly["pnl"]], textposition="outside"))
    fig.update_layout(
        title="Monthly PnL",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d", tickangle=-30),
        yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=60), height=300)
    return fig

def day_of_week_chart(df):
    if df.empty: return None
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    df_c = df.copy()
    df_c["day"] = df_c["trade_date"].dt.day_name()
    grp = df_c.groupby("day").agg(
        pnl=("pnl","sum"), trades=("result","count"),
        wins=("result", lambda x: (x=="Win").sum())
    ).reset_index()
    grp["win_rate"] = (grp["wins"]/grp["trades"]*100).round(1)
    grp["day"] = pd.Categorical(grp["day"], categories=days_order, ordered=True)
    grp = grp.sort_values("day")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=grp["day"], y=grp["pnl"],
        name="PnL %",
        marker_color=["#3fb950" if p >= 0 else "#f85149" for p in grp["pnl"]],
        text=[f"{p:+.1f}%" for p in grp["pnl"]], textposition="outside"))
    fig.update_layout(
        title="PnL by Day of Week",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=40), height=280)
    return fig

def pair_chart(df):
    if df.empty: return None
    grp = df.groupby("pair").agg(
        trades=("result","count"),
        wins=("result", lambda x: (x=="Win").sum())
    ).reset_index()
    grp["win_rate"] = (grp["wins"]/grp["trades"]*100).round(1)
    grp = grp.sort_values("win_rate", ascending=True)
    fig = go.Figure(go.Bar(
        x=grp["win_rate"], y=grp["pair"], orientation="h",
        marker_color=["#3fb950" if w>=50 else "#f85149" for w in grp["win_rate"]],
        text=[f"{w}% ({t})" for w,t in zip(grp["win_rate"],grp["trades"])],
        textposition="outside"))
    fig.update_layout(
        title="Win Rate by Pair",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d", range=[0,115]),
        yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=80,r=60,t=40,b=40), height=max(240, len(grp)*38))
    return fig

def session_chart(df):
    if df.empty: return None
    grp = df.groupby("session")["pnl"].sum().reset_index()
    fig = px.bar(grp, x="session", y="pnl",
        color="pnl", color_continuous_scale=["#f85149","#d29922","#3fb950"])
    fig.update_layout(
        title="PnL by Session",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=40), height=260,
        coloraxis_showscale=False)
    return fig

def strategy_chart(df):
    if df.empty: return None
    grp = df.groupby("strategy").agg(pnl=("pnl","sum"), trades=("result","count")).reset_index()
    grp = grp.sort_values("pnl", ascending=False)
    fig = go.Figure(go.Bar(
        x=grp["strategy"], y=grp["pnl"],
        marker_color=["#3fb950" if p>=0 else "#f85149" for p in grp["pnl"]],
        text=[f"{p:.1f}%" for p in grp["pnl"]], textposition="outside"))
    fig.update_layout(
        title="PnL by Strategy",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=60), height=280)
    return fig

def mood_chart(df):
    if df.empty or "mood" not in df.columns: return None
    grp = df.groupby("mood")["pnl"].agg(["sum","count"]).reset_index()
    grp.columns = ["mood","total_pnl","trades"]
    fig = go.Figure(go.Bar(
        x=grp["mood"], y=grp["total_pnl"],
        marker_color=["#3fb950" if p>=0 else "#f85149" for p in grp["total_pnl"]],
        text=[f"{p:+.1f}%\n({t} trades)" for p,t in zip(grp["total_pnl"],grp["trades"])],
        textposition="outside"))
    fig.update_layout(
        title="PnL by Trade Mood / Psychology",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=40), height=280)
    return fig

def get_insights(df):
    if df.empty: return []
    insights = []
    pair_wr = df.groupby("pair").apply(lambda x: (x["result"]=="Win").mean()*100).sort_values(ascending=False)
    if not pair_wr.empty:
        insights.append(f"🏆 Best Pair: **{pair_wr.index[0]}** ({pair_wr.iloc[0]:.0f}% win rate)")
    strat_pnl = df.groupby("strategy")["pnl"].sum().sort_values(ascending=False)
    if not strat_pnl.empty:
        insights.append(f"⚡ Best Strategy: **{strat_pnl.index[0]}** ({strat_pnl.iloc[0]:+.1f}% PnL)")
    sess_pnl = df.groupby("session")["pnl"].sum().sort_values(ascending=False)
    if not sess_pnl.empty:
        insights.append(f"🕐 Best Session: **{sess_pnl.index[0]}** ({sess_pnl.iloc[0]:+.1f}% PnL)")
    if "mood" in df.columns:
        mood_pnl = df.groupby("mood")["pnl"].sum().sort_values(ascending=False)
        if not mood_pnl.empty:
            insights.append(f"🧠 Best Mood to Trade: **{mood_pnl.index[0]}** ({mood_pnl.iloc[0]:+.1f}% PnL)")
    dow = df.copy()
    dow["day"] = dow["trade_date"].dt.day_name()
    best_day = dow.groupby("day")["pnl"].sum().sort_values(ascending=False)
    if not best_day.empty:
        insights.append(f"📅 Best Day: **{best_day.index[0]}** ({best_day.iloc[0]:+.1f}% PnL)")
    results = df.sort_values("trade_date")["result"].tolist()
    max_w, max_l, cw, cl = 0, 0, 0, 0
    for r in results:
        if r == "Win": cw+=1; cl=0; max_w=max(max_w,cw)
        elif r == "Loss": cl+=1; cw=0; max_l=max(max_l,cl)
        else: cw=0; cl=0
    insights.append(f"🔥 Max Win Streak: **{max_w}** | Max Loss Streak: **{max_l}**")
    dir_pnl = df.groupby("direction")["pnl"].sum() if "direction" in df.columns else pd.Series()
    for d,p in dir_pnl.items():
        insights.append(f"{'📈' if d=='Buy' else '📉'} {d} Total PnL: **{p:+.2f}%**")
    return insights

# ─────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────
def get_leaderboard():
    sb = get_supabase()
    res = sb.table("users").select("id,username").execute()
    users = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    rows = []
    for _, u in users.iterrows():
        df = load_trades(u["id"])
        if df.empty: continue
        total = len(df); wins = (df["result"]=="Win").sum()
        win_rate = round(wins/total*100,1)
        total_pnl = round(df["pnl"].fillna(0).sum(),2)
        avg_rr = round(df["rr"].dropna().mean(),2) if not df["rr"].dropna().empty else 0
        gp = df[df["pnl"]>0]["pnl"].sum()
        gl = abs(df[df["pnl"]<0]["pnl"].sum())
        pf = round(gp/gl,2) if gl else float("inf")
        rows.append({"Trader":u["username"],"Trades":total,
                     "Win Rate":f"{win_rate}%","Total PnL":f"{total_pnl:+.2f}%",
                     "Avg R:R":f"1:{avg_rr}","Profit Factor":pf,
                     "_pnl":total_pnl,"_wr":win_rate})
    if not rows: return pd.DataFrame()
    df_lb = pd.DataFrame(rows).sort_values("_pnl",ascending=False).reset_index(drop=True)
    df_lb.index += 1
    return df_lb

# ─────────────────────────────────────────────
# SECURITY QUESTIONS
# ─────────────────────────────────────────────
SECURITY_QUESTIONS = [
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What is your favorite trading pair?",
    "What city were you born in?",
    "What is your pet's name?",
]

# ─────────────────────────────────────────────
# LOGIN PAGE — No tabs, no expanders, no nesting
# ─────────────────────────────────────────────
def page_login():
    st.markdown("""
    <div style="text-align:center; margin-top:2rem; margin-bottom:1rem;">
        <h1 style="font-size:2.4rem; color:#58a6ff;">📈 Trading Journal</h1>
        <p style="color:#8b949e;">Track your edge. Build your discipline.</p>
    </div>""", unsafe_allow_html=True)

    # Which sub-page to show
    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        # Page switcher buttons
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🔑 Login", use_container_width=True, key="go_login"):
                st.session_state["auth_page"] = "login"
        with b2:
            if st.button("📝 Register", use_container_width=True, key="go_reg"):
                st.session_state["auth_page"] = "register"
        with b3:
            if st.button("🔓 Forgot", use_container_width=True, key="go_forgot"):
                st.session_state["auth_page"] = "forgot"

        st.markdown("---")
        auth_p = st.session_state.get("auth_page", "login")

        # ── LOGIN ──
        if auth_p == "login":
            st.markdown("#### 🔑 Login")
            uname = st.text_input("Username", placeholder="your_username", key="li_u")
            pw = st.text_input("Password", type="password", placeholder="••••••••", key="li_p")
            remember = st.checkbox("🔒 Remember Me", key="li_rem")
            if st.button("Login", use_container_width=True, key="li_btn"):
                if not uname.strip():
                    st.error("Please enter username.")
                else:
                    uid = login_user(uname, pw)
                    if uid:
                        st.session_state.update({
                            "user_id": uid,
                            "username": uname.strip(),
                            "active_account_id": None
                        })
                        if remember:
                            token = create_session(uid, uname.strip())
                            st.session_state["session_token"] = token
                            # Save to localStorage
                            st.components.v1.html(f"""
                            <script>
                            localStorage.setItem('tj_token', '{token}');
                            </script>
                            """, height=0)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        # ── REGISTER ──
        elif auth_p == "register":
            st.markdown("#### 📝 Create Account")
            nu = st.text_input("Username", placeholder="choose_username", key="re_u")
            np1 = st.text_input("Password", type="password", placeholder="min 6 chars", key="re_p")
            np2 = st.text_input("Confirm Password", type="password", key="re_p2")
            sq = st.selectbox("Security Question", SECURITY_QUESTIONS, key="re_sq")
            sa = st.text_input("Security Answer", placeholder="used to reset password", key="re_sa")
            if st.button("Create Account", use_container_width=True, key="re_btn"):
                err = None
                if len(nu.strip()) < 3: err = "Username must be at least 3 characters."
                elif len(np1) < 6: err = "Password must be at least 6 characters."
                elif np1 != np2: err = "Passwords don't match."
                elif not sa.strip(): err = "Please answer the security question."
                if err:
                    st.error(err)
                else:
                    ok, msg, _ = register_user(nu.strip(), np1, sq, sa)
                    if ok:
                        st.success(msg + " You can now log in.")
                        st.session_state["auth_page"] = "login"
                    else:
                        st.error(msg)

        # ── FORGOT PASSWORD ──
        elif auth_p == "forgot":
            st.markdown("#### 🔓 Reset Password")
            fp_u = st.text_input("Username", placeholder="your_username", key="fp_u")
            if fp_u.strip():
                row = get_security_question(fp_u.strip())
                if row is None:
                    st.error("Username not found.")
                elif not row[1]:
                    st.warning("No security question set. Please create a new account.")
                else:
                    st.info(f"Security Question: **{row[1]}**")
                    fp_a = st.text_input("Answer", key="fp_a")
                    fp_np = st.text_input("New Password", type="password", placeholder="min 6 chars", key="fp_np")
                    fp_np2 = st.text_input("Confirm Password", type="password", key="fp_np2")
                    if st.button("Reset Password", use_container_width=True, key="fp_btn"):
                        err = None
                        if len(fp_np) < 6: err = "Password must be at least 6 characters."
                        elif fp_np != fp_np2: err = "Passwords don't match."
                        if err:
                            st.error(err)
                        else:
                            if reset_password(fp_u.strip(), fp_a, fp_np):
                                st.success("Password reset successfully! Please log in.")
                                st.session_state["auth_page"] = "login"
                            else:
                                st.error("Wrong answer. Try again.")

# ─────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────
def render_navbar(username, active_account_name):
    is_admin = username == ADMIN_USERNAME
    dark = st.session_state.get("dark_mode", True)
    bg  = "#0a0e17" if dark else "#ffffff"
    bg2 = "#111827" if dark else "#f1f5f9"
    border = "#2d3748" if dark else "#e2e8f0"
    accent = "#3b82f6"
    text_c = "#f1f5f9" if dark else "#0f172a"
    muted  = "#94a3b8" if dark else "#64748b"

    # ── Top brand bar ──
    st.markdown(f"""
    <div style="background:{bg2}; border-bottom:2px solid {border};
        padding:0.7rem 1.5rem; display:flex; align-items:center;
        justify-content:space-between; margin:-1.5rem -2rem 0.8rem -2rem;
        box-shadow:0 2px 8px rgba(0,0,0,0.2);">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:1.3rem; font-weight:900; color:{accent}; letter-spacing:-0.02em;">
                📈 Trading Journal
            </span>
            <span style="background:{accent}22; color:{accent}; border:1px solid {accent}44;
                border-radius:20px; padding:2px 10px; font-size:0.72rem; font-weight:600;">
                💼 {active_account_name}
            </span>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="color:{muted}; font-size:0.82rem;">
                👤 <strong style="color:{text_c};">{username}</strong>
            </span>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Main nav — only 5 core pages ──
    n1,n2,n3,n4,n5 = st.columns(5)
    nav_pages = [
        (n1, "📊 Dashboard",  "dashboard"),
        (n2, "➕ New Trade",  "new_trade"),
        (n3, "📋 Trade Log",  "trade_log"),
        (n4, "💼 Accounts",   "accounts"),
        (n5, "🏆 Leaderboard","leaderboard"),
    ]
    cur_page = st.session_state.get("page","dashboard")
    for col, label, pg in nav_pages:
        with col:
            is_cur = cur_page == pg
            if st.button(label, use_container_width=True, key=f"nav_{pg}",
                         type="primary" if is_cur else "secondary"):
                st.session_state["page"] = pg; st.rerun()

    st.markdown("<hr style='margin:0.3rem 0 0.8rem 0; border-color:#2d3748;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def sidebar_filters(df):
    st.sidebar.markdown("### 🔍 Filters")
    min_d = df["trade_date"].min().date() if not df.empty else date.today()
    max_d = df["trade_date"].max().date() if not df.empty else date.today()
    dr = st.sidebar.date_input("Date Range", value=(min_d, max_d), key="f_date")
    pairs = ["All"] + sorted(df["pair"].unique().tolist()) if not df.empty else ["All"]
    pf = st.sidebar.selectbox("Pair", pairs, key="f_pair")
    strats = ["All"] + sorted(df["strategy"].dropna().unique().tolist()) if not df.empty else ["All"]
    sf = st.sidebar.selectbox("Strategy", strats, key="f_strat")
    df2 = df.copy()
    if not df2.empty:
        if len(dr) == 2:
            df2 = df2[(df2["trade_date"]>=pd.Timestamp(dr[0])) & (df2["trade_date"]<=pd.Timestamp(dr[1]))]
        if pf != "All": df2 = df2[df2["pair"]==pf]
        if sf != "All": df2 = df2[df2["strategy"]==sf]
    return df2

# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────
def show_dashboard(df, account_info):
    st.markdown("## 📊 Dashboard")
    stats = compute_stats(df)

    # ── Daily Notification Summary ──
    today_df = df[df["trade_date"].dt.date == date.today()] if not df.empty else pd.DataFrame()
    if not today_df.empty:
        today_trades = len(today_df)
        today_pnl = round(today_df["pnl"].fillna(0).sum(), 2)
        today_wins = (today_df["result"] == "Win").sum()
        today_wr = round(today_wins / today_trades * 100, 1)
        pnl_icon = "📈" if today_pnl >= 0 else "📉"
        notif_msg = (
            f"{pnl_icon} **Today's Summary** — "
            f"{today_trades} trades | "
            f"Win Rate: **{today_wr}%** ({today_wins}W/{today_trades - today_wins}L) | "
            f"PnL: **{today_pnl:+.2f}%**"
        )
        if account_info:
            acc_size = float(account_info.get("account_size", 0))
            currency = account_info.get("currency", "USD")
            money = round(acc_size * today_pnl / 100, 2)
            notif_msg += f" | **{currency} {money:+,.2f}**"
        st.markdown(f'<div class="notif-card">{notif_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="notif-card">📋 No trades logged today yet.</div>', unsafe_allow_html=True)

    # Daily loss limit warning
    if account_info and not today_df.empty:
        limit = float(account_info.get("daily_loss_limit", 2.0))
        today_pnl_val = round(today_df["pnl"].fillna(0).sum(), 2)
        if today_pnl_val <= -limit:
            st.error(f"🚨 **DAILY LOSS LIMIT REACHED!** Today: {today_pnl_val:.2f}% (Limit: -{limit}%) — STOP TRADING NOW!")
        elif today_pnl_val < 0:
            remaining = limit + today_pnl_val
            st.warning(f"⚠️ Today PnL: {today_pnl_val:.2f}% | Remaining buffer: **{remaining:.2f}%**")

    if not stats:
        st.info("No trades yet. Go to **💼 Accounts** → create account → **➕ New Trade**")
        return

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Trades", stats["total"])
    c2.metric("Win Rate", f"{stats['win_rate']}%", delta=f"{stats['wins']}W / {stats['losses']}L")
    c3.metric("Profit Factor", stats["profit_factor"])
    c4.metric("Avg R:R", f"1:{stats['avg_rr']}")
    c5.metric("Max Drawdown", f"{stats['max_drawdown']}%", delta_color="inverse")

    total_pnl_pct = round(stats["equity"].iloc[-1], 2) if len(stats["equity"]) > 0 else 0
    if account_info:
        acc_size = float(account_info.get("account_size", 0))
        currency = account_info.get("currency", "USD")
        pnl_money = round(acc_size * total_pnl_pct / 100, 2)
        c6.metric(f"Total PnL ({currency})", f"{pnl_money:+,.2f}", delta=f"{total_pnl_pct:+.2f}%")
    else:
        c6.metric("Total PnL %", f"{total_pnl_pct:+.2f}%")

    # Commission + Swap summary
    if not df.empty:
        total_comm = round(df["commission"].fillna(0).sum(), 4) if "commission" in df.columns else 0
        total_swap = round(df["swap"].fillna(0).sum(), 4) if "swap" in df.columns else 0
        total_net  = round(df["net_pnl"].fillna(0).sum(), 4) if "net_pnl" in df.columns else total_pnl_pct
        if total_comm != 0 or total_swap != 0:
            acc_sz_d = float(account_info.get("account_size",10000)) if account_info else 10000
            curr_d = account_info.get("currency","USD") if account_info else "USD"
            comm_usd = round(acc_sz_d * total_comm / 100, 2)
            swap_usd = round(acc_sz_d * total_swap / 100, 2)
            net_usd  = round(acc_sz_d * total_net / 100, 2)
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("💸 Total Commission", f"{curr_d} {comm_usd:,.2f}", delta_color="inverse")
            cc2.metric("🔄 Total Swap", f"{curr_d} {swap_usd:+,.2f}", delta_color="inverse")
            cc3.metric("✅ Net PnL (after fees)", f"{curr_d} {net_usd:+,.2f}",
                       delta=f"Gross: {total_pnl_pct:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(equity_chart(stats["dates"], stats["equity"], stats["drawdown"]),
                    use_container_width=True)

    # PnL Calendar on dashboard too
    show_pnl_calendar(df)

    col1, col2 = st.columns(2)
    with col1:
        fig = monthly_calendar_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = day_of_week_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = pair_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with col4:
        fig = session_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        fig = strategy_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with col6:
        fig = mood_chart(df)
        if fig: st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 💡 Performance Insights")
    for ins in get_insights(df):
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NEW TRADE PAGE
# ─────────────────────────────────────────────
PAIRS = ["EURUSD","GBPUSD","USDJPY","USDCHF","AUDUSD","NZDUSD","USDCAD",
         "GBPJPY","EURJPY","XAUUSD","BTCUSD","ETHUSD","US30","NAS100","SPX500","Custom"]
SESSIONS = ["Asia","London","New York","Overlap (London/NY)"]
RESULTS = ["Win","Loss","BE"]
DIRECTIONS = ["Buy","Sell"]
MOODS = ["Confident","Neutral","Anxious","FOMO","Revenge","Bored","Excited"]

def show_trade_form(uid, aid):
    st.markdown("## ➕ Log New Trade")
    if not aid:
        st.warning("⚠️ No account selected. Go to **💼 Accounts** first.")
        return

    with st.form("trade_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            pc = st.selectbox("Pair", PAIRS)
            pair = st.text_input("Custom Pair", placeholder="e.g. GBPCAD").upper() if pc == "Custom" else pc
            tdate = st.date_input("Date", value=date.today())
            session = st.selectbox("Session", SESSIONS)
            direction = st.selectbox("Direction 📈📉", DIRECTIONS)
        with c2:
            strategy = st.text_input("Strategy", placeholder="e.g. ICT OB, Breakout")
            entry = st.number_input("Entry Price", min_value=0.0, value=None, placeholder="e.g. 1.08500", format="%.5f", step=0.00001)
            sl = st.number_input("Stop Loss", min_value=0.0, value=None, placeholder="e.g. 1.08200", format="%.5f", step=0.00001)
            tp = st.number_input("Take Profit", min_value=0.0, value=None, placeholder="e.g. 1.09100", format="%.5f", step=0.00001)
        with c3:
            risk_pct = st.number_input("Risk %", min_value=0.01, max_value=100.0, value=1.0, step=0.1, format="%.2f")
            result = st.selectbox("Result", RESULTS)
            mood = st.selectbox("Mood / Psychology 🧠", MOODS)
            commission = st.number_input("💸 Commission ($)", min_value=0.0, value=0.0, step=0.01, format="%.2f",
                                         help="Broker commission in dollars (e.g. 3.50)")
            swap = st.number_input("🔄 Swap ($)", min_value=-10000.0, max_value=10000.0, value=0.0, step=0.01, format="%.2f",
                                   help="Overnight swap fee in dollars (negative = paid, positive = received)")
            screenshot = st.file_uploader("📸 Screenshot", type=["png","jpg","jpeg","webp"])

        st.markdown("**📝 Notes** *(supports **bold**, *italic*, - bullets, ## headings)*")
        notes = st.text_area("", placeholder="## Setup\n- Trend: Bullish\n- Entry: OB retest\n\n**Emotions:** Confident\n\n**Lesson:** Waited patiently", height=120, key="trade_notes_rich", label_visibility="collapsed")
        if notes:
            with st.expander("👁️ Preview Notes", expanded=False):
                st.markdown(notes)
        tags = st.text_input("🏷️ Tags", placeholder="#ict #breakout #revenge", key="trade_tags")

        if entry and sl and tp and entry > 0 and sl > 0 and tp > 0:
            rr_p = calc_rr(entry, sl, tp)
            pnl_p = calc_pnl(result, risk_pct, rr_p)
            acc_sz_prev = float(account_info.get("account_size", 10000)) if account_info else 10000.0
            curr_prev = account_info.get("currency","USD") if account_info else "USD"
            comm_pct_prev = (commission or 0) / acc_sz_prev * 100 if acc_sz_prev > 0 else 0
            swap_pct_prev = (swap or 0) / acc_sz_prev * 100 if acc_sz_prev > 0 else 0
            net_p = round((pnl_p or 0) - comm_pct_prev - swap_pct_prev, 4)
            net_money = round(acc_sz_prev * net_p / 100, 2)
            p1,p2,p3,p4 = st.columns(4)
            p1.info(f"**R:R** → 1:{rr_p}" if rr_p else "**R:R** → N/A")
            icon = "✅" if (pnl_p or 0)>0 else ("❌" if (pnl_p or 0)<0 else "⚖️")
            p2.info(f"**Gross PnL** → {icon} {pnl_p:+.2f}%" if pnl_p is not None else "**PnL** → N/A")
            net_icon = "✅" if net_p > 0 else ("❌" if net_p < 0 else "⚖️")
            p3.info(f"**Net PnL** → {net_icon} {curr_prev} {net_money:+.2f}")
            p4.info(f"**{direction}** | {mood}")

        submitted = st.form_submit_button("💾 Save Trade", use_container_width=True)

    if submitted:
        if not pair: st.error("Enter pair.")
        elif not entry or not sl or not tp or entry==0 or sl==0 or tp==0:
            st.error("Entry, SL, TP required and must be non-zero.")
        else:
            ss_bytes = screenshot.read() if screenshot else None
            tag_str = tags.strip() if tags else ""
            full_notes = (notes + " | Tags: " + tag_str) if tag_str else notes
            acc_sz = float(account_info.get("account_size", 10000)) if account_info else 10000.0
            save_trade(uid, aid, pair, tdate, session, strategy, direction,
                       entry, sl, tp, risk_pct, result, mood, full_notes, ss_bytes,
                       commission=commission, swap=swap, account_size=acc_sz)
            st.success(f"✅ Saved — {direction} {pair} | {result} | Net PnL: {round((calc_pnl(result,risk_pct,calc_rr(entry,sl,tp)) or 0) - commission - swap, 4):+.4f}%")

# ─────────────────────────────────────────────
# TRADE LOG PAGE
# ─────────────────────────────────────────────
def show_trade_log(df, uid):
    st.markdown("## 📋 Trade Log")
    if df.empty:
        st.info("No trades found for current filters.")
        return

    # Search bar
    search = st.text_input("🔍 Search", placeholder="Search pair, strategy, result...", key="tl_search")
    if search:
        mask = df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
        df = df[mask]

    disp_cols = ["trade_date","pair","direction","session","strategy","entry","stop_loss","take_profit","risk_pct","result","rr","pnl","mood"]
    df_d = df[disp_cols].copy()
    df_d["trade_date"] = df_d["trade_date"].dt.strftime("%Y-%m-%d")
    df_d.columns = ["Date","Pair","Dir","Session","Strategy","Entry","SL","TP","Risk%","Result","R:R","PnL%","Mood"]
    st.dataframe(df_d.reset_index(drop=True), use_container_width=True, height=360)

    # Pair accuracy
    st.markdown("### 📌 Pair-wise Accuracy")
    ptbl = df.groupby("pair").agg(
        Trades=("result","count"),
        Wins=("result", lambda x: (x=="Win").sum()),
        Losses=("result", lambda x: (x=="Loss").sum()),
        Total_PnL=("pnl","sum"), Avg_RR=("rr","mean")
    ).reset_index()
    ptbl["Win Rate"] = (ptbl["Wins"]/ptbl["Trades"]*100).round(1).astype(str)+"%"
    ptbl["Total_PnL"] = ptbl["Total_PnL"].round(2).astype(str)+"%"
    ptbl["Avg_RR"] = ptbl["Avg_RR"].round(2)
    st.dataframe(ptbl.rename(columns={"pair":"Pair"}), use_container_width=True)

    # Export
    csv = df_d.to_csv(index=False).encode()
    st.download_button("⬇️ Export CSV", csv, "trades.csv", "text/csv")

    st.markdown("---")
    col_edit, col_del, col_ss = st.columns(3)

    trade_labels = [
        f"#{r['id']} — {r['trade_date'].strftime('%Y-%m-%d')} | {r['pair']} | {r['result']}"
        for _, r in df.iterrows()
    ]

    # ── EDIT TRADE ──
    with col_edit:
        st.markdown("### ✏️ Edit Trade")
        sel_edit = st.selectbox("Select", trade_labels, key="edit_sel")
        if st.button("✏️ Edit Selected", key="btn_edit_open", use_container_width=True):
            idx = trade_labels.index(sel_edit)
            st.session_state["edit_trade_id"] = df.iloc[idx]["id"]

    # ── DELETE TRADE ──
    with col_del:
        st.markdown("### 🗑️ Delete Trade")
        sel_del = st.selectbox("Select", trade_labels, key="del_sel")
        if st.button("🗑️ Delete Selected", key="btn_del_req", use_container_width=True):
            idx = trade_labels.index(sel_del)
            st.session_state["confirm_delete_id"] = df.iloc[idx]["id"]
            st.session_state["confirm_delete_label"] = sel_del

    # ── SCREENSHOT VIEW ──
    with col_ss:
        st.markdown("### 📸 Screenshot")
        # Support both old binary and new URL based screenshots
        ss_col = "screenshot_url" if "screenshot_url" in df.columns else "screenshot"
        df_ss = df[df[ss_col].notna() & (df[ss_col] != "")]
        if not df_ss.empty:
            ss_labels = [
                f"#{int(r['id'])} — {r['trade_date'].strftime('%Y-%m-%d')} | {r['pair']} | {r['result']}"
                for _, r in df_ss.iterrows()
            ]
            sel_ss = st.selectbox("Select Trade", ss_labels, key="ss_sel")
            if sel_ss:
                idx = ss_labels.index(sel_ss)
                ss_val = df_ss.iloc[idx][ss_col]
                if ss_val:
                    if isinstance(ss_val, str) and ss_val.startswith("http"):
                        # New URL based screenshot
                        st.image(ss_val, use_container_width=True)
                        st.markdown(f"[🔗 Open Full Size]({ss_val})", unsafe_allow_html=False)
                    else:
                        # Old binary screenshot
                        st.image(ss_val, use_container_width=True)
        else:
            st.info("📸 No screenshots yet. Upload when logging a trade!")

    # Delete confirmation popup
    if st.session_state.get("confirm_delete_id"):
        st.warning(f"⚠️ Delete **{st.session_state.get('confirm_delete_label')}**? Cannot be undone!")
        y,n = st.columns(2)
        with y:
            if st.button("✅ Yes, Delete", key="del_yes", use_container_width=True):
                delete_trade(st.session_state["confirm_delete_id"])
                st.session_state.pop("confirm_delete_id", None)
                st.session_state.pop("confirm_delete_label", None)
                st.success("Deleted."); st.rerun()
        with n:
            if st.button("❌ Cancel", key="del_no", use_container_width=True):
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()

    # Edit trade form
    if st.session_state.get("edit_trade_id"):
        tid = st.session_state["edit_trade_id"]
        t = get_trade_by_id(tid)
        if t:
            st.markdown("---")
            st.markdown(f"### ✏️ Editing Trade #{tid} — {t['pair']}")
            with st.form(f"edit_form_{tid}"):
                e1,e2,e3 = st.columns(3)
                with e1:
                    pc = st.selectbox("Pair", PAIRS, index=PAIRS.index(t["pair"]) if t["pair"] in PAIRS else len(PAIRS)-1, key="ep")
                    ep = st.text_input("Custom Pair", value=t["pair"], key="epc") if pc=="Custom" else pc
                    ed = st.date_input("Date", value=pd.to_datetime(t["trade_date"]).date(), key="ed")
                    ess = st.selectbox("Session", SESSIONS, index=SESSIONS.index(t["session"]) if t["session"] in SESSIONS else 0, key="ess")
                    edir = st.selectbox("Direction", DIRECTIONS, index=DIRECTIONS.index(t["direction"]) if t["direction"] in DIRECTIONS else 0, key="edir")
                with e2:
                    estrat = st.text_input("Strategy", value=t["strategy"] or "", key="estrat")
                    eentry = st.number_input("Entry", value=float(t["entry"] or 0), format="%.5f", key="eentry")
                    esl = st.number_input("Stop Loss", value=float(t["stop_loss"] or 0), format="%.5f", key="esl")
                    etp = st.number_input("Take Profit", value=float(t["take_profit"] or 0), format="%.5f", key="etp")
                with e3:
                    erisk = st.number_input("Risk %", value=float(t["risk_pct"] or 1), format="%.2f", key="erisk")
                    eres = st.selectbox("Result", RESULTS, index=RESULTS.index(t["result"]) if t["result"] in RESULTS else 0, key="eres")
                    emood = st.selectbox("Mood", MOODS, index=MOODS.index(t["mood"]) if t["mood"] in MOODS else 1, key="emood")
                enotes = st.text_area("Notes", value=t["notes"] or "", key="enotes")
                ec1, ec2 = st.columns(2)
                with ec1:
                    ecommission = st.number_input("💸 Commission %", value=float(t.get("commission") or 0), format="%.4f", key="ecomm")
                with ec2:
                    eswap = st.number_input("🔄 Swap %", value=float(t.get("swap") or 0), format="%.4f", key="eswap")
                save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if save_edit:
                update_trade(tid, ep, ed, ess, estrat, edir, eentry, esl, etp, erisk, eres, emood, enotes,
                           commission=ecommission, swap=eswap)
                st.session_state.pop("edit_trade_id", None)
                st.success("✅ Trade updated!"); st.rerun()

            if st.button("❌ Cancel Edit", key="cancel_edit"):
                st.session_state.pop("edit_trade_id", None); st.rerun()

# ─────────────────────────────────────────────
# ACCOUNTS PAGE
# ─────────────────────────────────────────────
def show_accounts(uid):
    st.markdown("## 💼 Trading Accounts")
    accounts = get_accounts(uid)

    # Toggle add form visibility — no expander, no nesting issues
    if st.button("➕ Add New Account", key="toggle_add_acc"):
        st.session_state["show_add_acc"] = not st.session_state.get("show_add_acc", False)

    if st.session_state.get("show_add_acc", False):
        st.markdown("#### New Account Details")
        a1, a2 = st.columns(2)
        with a1:
            aname = st.text_input("Account Name *", placeholder="e.g. Funded Account", key="acc_name")
            broker = st.text_input("Broker", placeholder="e.g. ICMarkets", key="acc_broker")
        with a2:
            asize = st.number_input("Account Size *", min_value=0.0, value=10000.0, step=100.0, format="%.2f", key="acc_size")
            curr = st.selectbox("Currency", ["USD","EUR","GBP","INR","AUD","CAD"], key="acc_curr")
            dloss = st.number_input("Daily Loss Limit %", min_value=0.1, max_value=100.0, value=2.0, step=0.5, format="%.1f", key="acc_dloss")

        if st.button("💾 Create Account", key="btn_create_acc", use_container_width=True):
            if not st.session_state.get("acc_name","").strip():
                st.error("Account name is required.")
            elif st.session_state.get("acc_size", 0) <= 0:
                st.error("Account size must be greater than 0.")
            else:
                create_account(
                    uid,
                    st.session_state["acc_name"].strip(),
                    st.session_state.get("acc_broker",""),
                    st.session_state["acc_size"],
                    st.session_state["acc_curr"],
                    st.session_state["acc_dloss"]
                )
                st.session_state["show_add_acc"] = False
                st.success("✅ Account created!")
                st.rerun()

        st.markdown("---")

    if accounts.empty:
        st.info("No accounts yet. Click 'Add New Account' above.")
        return

    st.markdown("### Your Accounts")

    # Position Size Calculator
    with st.expander("🧮 Position Size Calculator"):
        acc_options = accounts["account_name"].tolist()
        sel_acc = st.selectbox("Account", acc_options, key="psc_acc")
        acc_row = accounts[accounts["account_name"]==sel_acc].iloc[0]
        p1,p2,p3 = st.columns(3)
        with p1:
            psc_entry = st.number_input("Entry Price", min_value=0.0, value=None, placeholder="1.08500", format="%.5f", key="psc_e")
            psc_sl = st.number_input("Stop Loss", min_value=0.0, value=None, placeholder="1.08200", format="%.5f", key="psc_sl")
        with p2:
            psc_risk = st.number_input("Risk %", min_value=0.01, value=1.0, step=0.1, format="%.2f", key="psc_r")
        with p3:
            if psc_entry and psc_sl and psc_entry > 0 and psc_sl > 0:
                pip_risk = abs(psc_entry - psc_sl)
                account_risk = acc_row["account_size"] * (psc_risk/100)
                if pip_risk > 0:
                    lot_size = account_risk / pip_risk
                    st.metric("Account Risk Amount", f"{acc_row['currency']} {account_risk:,.2f}")
                    st.metric("Pip Risk", f"{pip_risk:.5f}")
                    st.metric("Lot Size (units)", f"{lot_size:,.0f}")

    st.markdown("---")
    for _, acc in accounts.iterrows():
        df_acc = load_trades(uid, acc["id"])
        trade_count = len(df_acc)
        total_pnl = round(df_acc["pnl"].fillna(0).sum(), 2) if not df_acc.empty else 0
        is_active = st.session_state.get("active_account_id") == acc["id"]

        c1,c2 = st.columns([5,1])
        with c1:
            active_tag = "  🔵 ACTIVE" if is_active else ""
            acc_size = float(acc["account_size"])
            currency = acc["currency"]
            pnl_money = round(acc_size * total_pnl / 100, 2)
            current_equity = round(acc_size + pnl_money, 2)
            pnl_color_tag = "🟢" if total_pnl >= 0 else "🔴"
            st.markdown(f"#### 💼 {acc['account_name']}{active_tag}")
            st.caption(
                f"🏦 **{acc['broker'] or 'N/A'}**  |  "
                f"💰 Initial: **{currency} {acc_size:,.0f}**  |  "
                f"📈 Current Equity: **{currency} {current_equity:,.2f}**  |  "
                f"{pnl_color_tag} PnL: **{currency} {pnl_money:+,.2f} ({total_pnl:+.2f}%)**  |  "
                f"📊 **{trade_count} trades**  |  "
                f"🛑 Daily Limit: **{acc.get('daily_loss_limit',2.0)}%**"
            )
        with c2:
            if st.button("✅ Active" if is_active else "Select", key=f"sel_{acc['id']}", use_container_width=True):
                st.session_state["active_account_id"] = acc["id"]
                st.session_state["active_account_name"] = acc["account_name"]
                st.rerun()
            if st.button("🗑️", key=f"delacc_{acc['id']}", use_container_width=True):
                delete_account(acc["id"])
                if st.session_state.get("active_account_id") == acc["id"]:
                    st.session_state["active_account_id"] = None
                st.rerun()
        st.divider()

# ─────────────────────────────────────────────
# LEADERBOARD PAGE
# ─────────────────────────────────────────────
def show_leaderboard():
    st.markdown("## 🏆 Leaderboard")
    st.caption("Rankings based on Total PnL — all accounts combined")
    df_lb = get_leaderboard()
    if df_lb.empty:
        st.info("No traders with trades yet."); return

    top3 = df_lb.head(3)
    medals = ["🥇","🥈","🥉"]
    cols = st.columns(min(3, len(top3)))
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.metric(f"{medals[i]} {row['Trader']}", row["Total PnL"], delta=f"WR: {row['Win Rate']}")

    st.markdown("<br>", unsafe_allow_html=True)
    df_show = df_lb[["Trader","Trades","Win Rate","Total PnL","Avg R:R","Profit Factor"]].copy()
    df_show.insert(0,"Rank", [medals[i] if i<3 else f"#{i+1}" for i in range(len(df_show))])
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    fig = go.Figure(go.Bar(
        x=df_lb["Trader"], y=df_lb["_pnl"],
        marker_color=["#3fb950" if p>=0 else "#f85149" for p in df_lb["_pnl"]],
        text=[f"{p:+.1f}%" for p in df_lb["_pnl"]], textposition="outside"))
    fig.update_layout(
        title="PnL Comparison",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        margin=dict(l=40,r=20,t=40,b=40), height=300)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# WEEKLY REVIEW PAGE
# ─────────────────────────────────────────────
def show_weekly_review(uid):
    st.markdown("## 📝 Weekly Review")
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    # Check if editing existing review
    editing_review = st.session_state.get("edit_review_id")
    reviews = load_weekly_reviews(uid)

    if editing_review:
        edit_row = reviews[reviews["id"] == editing_review]
        if not edit_row.empty:
            r = edit_row.iloc[0]
            st.markdown(f"### ✏️ Editing Review — Week of {r['week_start']}")
            week = st.date_input("Week Starting", value=pd.to_datetime(r["week_start"]).date(), key="wr_week_e")
            score = st.slider("Score", 1, 10, int(r["score"]), key="wr_score_e")
            went_well = st.text_area("✅ What Went Well?", value=r["what_went_well"] or "", height=100, key="wr_well_e")
            improve = st.text_area("❌ What to Improve?", value=r["what_to_improve"] or "", height=100, key="wr_imp_e")
            lessons = st.text_area("📚 Key Lessons", value=r["lessons"] or "", height=80, key="wr_les_e")
            col_s, col_c = st.columns(2)
            with col_s:
                if st.button("💾 Save Changes", use_container_width=True, key="wr_save_edit"):
                    save_weekly_review(uid, week, went_well, improve, lessons, score)
                    st.session_state.pop("edit_review_id", None)
                    st.success("✅ Review updated!"); st.rerun()
            with col_c:
                if st.button("❌ Cancel", use_container_width=True, key="wr_cancel_edit"):
                    st.session_state.pop("edit_review_id", None); st.rerun()
            st.markdown("---")
            return

    # New review form
    st.markdown("### ➕ New Review")
    with st.form("weekly_review_form", clear_on_submit=True):
        c1,c2 = st.columns(2)
        with c1:
            week = st.date_input("Week Starting (Monday)", value=monday, key="wr_week")
            score = st.slider("Overall Week Score", 1, 10, 5, key="wr_score",
                              help="1=Terrible, 10=Perfect")
        with c2:
            went_well = st.text_area("✅ What Went Well?", placeholder="Good setups, discipline, patience...", height=100, key="wr_well")
            improve = st.text_area("❌ What to Improve?", placeholder="FOMO trades, overtrading...", height=100, key="wr_imp")
        lessons = st.text_area("📚 Key Lessons Learned", placeholder="Rules I broke, insights...", height=80, key="wr_les")
        sub = st.form_submit_button("💾 Save Review", use_container_width=True)

    if sub:
        save_weekly_review(uid, week, went_well, improve, lessons, score)
        st.success("✅ Weekly review saved!"); st.rerun()

    st.markdown("---")
    st.markdown("### 📖 Past Reviews")
    if reviews.empty:
        st.info("No reviews yet.")
        return

    for _, r in reviews.iterrows():
        score_stars = "⭐" * int(r["score"])
        with st.expander(f"Week of {r['week_start']} — Score: {score_stars} ({r['score']}/10)"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ What Went Well:**")
                st.write(r["what_went_well"] or "—")
                st.markdown("**❌ What to Improve:**")
                st.write(r["what_to_improve"] or "—")
            with c2:
                st.markdown("**📚 Lessons Learned:**")
                st.write(r["lessons"] or "—")
            if st.button(f"✏️ Edit this Review", key=f"edit_wr_{r['id']}", use_container_width=False):
                st.session_state["edit_review_id"] = r["id"]
                st.rerun()

# ─────────────────────────────────────────────
# PNL CALENDAR
# ─────────────────────────────────────────────
def show_pnl_calendar(df):
    st.markdown("### 📅 PnL Calendar")

    if df.empty:
        st.info("No trades yet to show on calendar.")
        return

    today = date.today()

    # Month selector
    col_m, col_y, _ = st.columns([2, 2, 4])
    with col_m:
        months = ["January","February","March","April","May","June",
                  "July","August","September","October","November","December"]
        sel_month = st.selectbox("Month", months, index=today.month - 1, key="cal_month")
    with col_y:
        years = sorted(df["trade_date"].dt.year.unique().tolist(), reverse=True)
        if today.year not in years:
            years.insert(0, today.year)
        sel_year = st.selectbox("Year", years, index=0, key="cal_year")

    month_num = months.index(sel_month) + 1

    # Build daily PnL map
    df_cal = df.copy()
    df_cal = df_cal[
        (df_cal["trade_date"].dt.month == month_num) &
        (df_cal["trade_date"].dt.year == sel_year)
    ]

    daily_map = {}
    if not df_cal.empty:
        grp = df_cal.groupby(df_cal["trade_date"].dt.day).agg(
            pnl=("pnl", "sum"),
            trades=("result", "count"),
            wins=("result", lambda x: (x == "Win").sum()),
            losses=("result", lambda x: (x == "Loss").sum()),
        )
        for day, row in grp.iterrows():
            daily_map[day] = row

    # Calendar grid
    cal = calendar.monthcalendar(sel_year, month_num)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    dark = st.session_state.get("dark_mode", True)
    bg_card = "#161b22" if dark else "#ffffff"
    bg_empty = "#0d1117" if dark else "#f6f8fa"
    border_c = "#30363d" if dark else "#d0d7de"
    text_c = "#e6edf3" if dark else "#24292f"
    muted_c = "#8b949e" if dark else "#57606a"

    # Header row
    header_cols = st.columns(7)
    for i, dn in enumerate(day_names):
        color = "#f85149" if dn == "Sun" else (muted_c)
        header_cols[i].markdown(
            f"<div style='text-align:center; color:{color}; font-weight:700; "
            f"padding:4px; font-size:0.85rem;'>{dn}</div>",
            unsafe_allow_html=True
        )

    # Weeks
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown(
                        f"<div style='background:{bg_empty}; border:1px solid {border_c}; "
                        f"border-radius:8px; height:80px; margin:2px;'></div>",
                        unsafe_allow_html=True
                    )
                else:
                    is_today = (day == today.day and month_num == today.month and sel_year == today.year)
                    today_ring = f"box-shadow: 0 0 0 2px #58a6ff;" if is_today else ""

                    if day in daily_map:
                        row = daily_map[day]
                        pnl = round(row["pnl"], 2)
                        trades = int(row["trades"])
                        wins = int(row["wins"])
                        losses = int(row["losses"])

                        if pnl > 0:
                            bg = "#1a3a2a"
                            pnl_color = "#3fb950"
                            border = "#2ea043"
                        elif pnl < 0:
                            bg = "#3a1a1a"
                            pnl_color = "#f85149"
                            border = "#da3633"
                        else:
                            bg = "#2a2a1a"
                            pnl_color = "#d29922"
                            border = "#d29922"

                        # Get account size for $ calculation
                        aid_active = st.session_state.get("active_account_id")
                        acc_inf = get_account_info(aid_active) if aid_active else None
                        acc_sz = float(acc_inf.get("account_size", 0)) if acc_inf else 0
                        curr = acc_inf.get("currency", "USD") if acc_inf else "USD"
                        money_val = round(acc_sz * pnl / 100, 2) if acc_sz > 0 else None
                        money_str = f"{curr} {money_val:+,.0f}" if money_val is not None else f"{pnl:+.1f}%"

                        st.markdown(f"""
                        <div style='background:{bg}; border:1px solid {border};
                            border-radius:8px; padding:6px 4px; height:80px;
                            margin:2px; text-align:center; {today_ring}'>
                            <div style='color:{text_c}; font-weight:700; font-size:0.95rem;'>{day}</div>
                            <div style='color:{pnl_color}; font-weight:800; font-size:0.85rem;'>{money_str}</div>
                            <div style='color:{muted_c}; font-size:0.7rem;'>{trades}T · {wins}W {losses}L</div>
                        </div>""", unsafe_allow_html=True)

                    else:
                        day_color = "#f85149" if i == 6 else text_c
                        st.markdown(f"""
                        <div style='background:{bg_card}; border:1px solid {border_c};
                            border-radius:8px; padding:6px 4px; height:80px;
                            margin:2px; text-align:center; {today_ring}'>
                            <div style='color:{day_color}; font-weight:500; font-size:0.95rem;'>{day}</div>
                            <div style='color:{muted_c}; font-size:0.7rem; margin-top:8px;'>—</div>
                        </div>""", unsafe_allow_html=True)

    # Monthly summary below calendar
    st.markdown("<br>", unsafe_allow_html=True)
    if not df_cal.empty:
        total_pnl = round(df_cal["pnl"].fillna(0).sum(), 2)
        total_trades = len(df_cal)
        win_days = sum(1 for d in daily_map.values() if d["pnl"] > 0)
        loss_days = sum(1 for d in daily_map.values() if d["pnl"] < 0)
        wr = round((df_cal["result"] == "Win").sum() / total_trades * 100, 1)

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Month PnL", f"{total_pnl:+.2f}%")
        s2.metric("Total Trades", total_trades)
        s3.metric("Win Rate", f"{wr}%")
        s4.metric("Green Days", f"🟢 {win_days}")
        s5.metric("Red Days", f"🔴 {loss_days}")
    else:
        st.info(f"No trades in {sel_month} {sel_year}.")

# ─────────────────────────────────────────────
# GOALS PAGE
# ─────────────────────────────────────────────
def show_goals(uid, df):
    st.markdown("## 🎯 Goals Tracker")
    month_str = date.today().strftime("%Y-%m")
    month_label = date.today().strftime("%B %Y")

    st.markdown(f"### 📅 {month_label} Goals")

    goal = get_goal(uid, month_str)

    col1, col2 = st.columns([2, 1])
    with col2:
        st.markdown("#### Set Goals")
        t_pnl = st.number_input("Target PnL %", value=float(goal["target_pnl"]) if goal else 5.0, step=0.5, format="%.1f", key="g_pnl")
        t_trades = st.number_input("Target Trades", value=int(goal["target_trades"]) if goal else 20, step=1, key="g_trades")
        t_wr = st.number_input("Target Win Rate %", value=float(goal["target_winrate"]) if goal else 60.0, step=1.0, format="%.1f", key="g_wr")
        if st.button("💾 Save Goals", use_container_width=True, key="save_goal"):
            save_goal(uid, month_str, t_pnl, t_trades, t_wr)
            st.success("Goals saved!"); st.rerun()

    with col1:
        if goal and not df.empty:
            # Filter this month
            df_month = df[df["trade_date"].dt.strftime("%Y-%m") == month_str]
            actual_pnl = round(df_month["pnl"].fillna(0).sum(), 2)
            actual_trades = len(df_month)
            actual_wr = round((df_month["result"] == "Win").sum() / len(df_month) * 100, 1) if len(df_month) > 0 else 0

            t_pnl_v = float(goal["target_pnl"])
            t_tr_v = int(goal["target_trades"])
            t_wr_v = float(goal["target_winrate"])

            # PnL Progress
            pnl_pct = min(actual_pnl / t_pnl_v * 100, 100) if t_pnl_v > 0 else 0
            st.markdown("#### PnL Progress")
            st.progress(max(pnl_pct / 100, 0))
            pnl_color = "green" if actual_pnl >= 0 else "red"
            st.markdown(f"**{actual_pnl:+.2f}%** / {t_pnl_v:.1f}% &nbsp;|&nbsp; {pnl_pct:.0f}% complete")

            st.markdown("<br>", unsafe_allow_html=True)

            # Trades Progress
            tr_pct = min(actual_trades / t_tr_v * 100, 100) if t_tr_v > 0 else 0
            st.markdown("#### Trades Progress")
            st.progress(tr_pct / 100)
            st.markdown(f"**{actual_trades}** / {t_tr_v} trades &nbsp;|&nbsp; {tr_pct:.0f}% complete")

            st.markdown("<br>", unsafe_allow_html=True)

            # Win Rate Progress
            wr_pct = min(actual_wr / t_wr_v * 100, 100) if t_wr_v > 0 else 0
            st.markdown("#### Win Rate Progress")
            st.progress(wr_pct / 100)
            st.markdown(f"**{actual_wr:.1f}%** / {t_wr_v:.1f}% &nbsp;|&nbsp; {wr_pct:.0f}% complete")

            st.markdown("<br>", unsafe_allow_html=True)

            # Summary card
            if actual_pnl >= t_pnl_v and actual_trades >= t_tr_v and actual_wr >= t_wr_v:
                st.success("🏆 All goals achieved this month! Excellent work!")
            elif actual_pnl < 0:
                st.error("📉 PnL is negative — review your trades and strategy!")
            else:
                st.info(f"💪 Keep going! {t_pnl_v - actual_pnl:.1f}% more PnL needed to hit target.")
        else:
            st.info("Set your goals on the right and start logging trades!")

    # Full Calendar view
    st.markdown("---")
    show_pnl_calendar(df)

# ─────────────────────────────────────────────
# PRE-TRADE CHECKLIST PAGE
# ─────────────────────────────────────────────
DEFAULT_CHECKLIST = [
    "Trend direction confirmed (Higher TF)",
    "Key level / structure identified",
    "Entry trigger present (OB/FVG/Pattern)",
    "Stop Loss placed at valid level",
    "Risk % calculated and within limit",
    "R:R is minimum 1:2",
    "News/session risk checked",
    "Not trading out of FOMO or revenge",
    "Trading plan followed"
]

def show_checklist(uid):
    st.markdown("## ✅ Pre-Trade Checklist")
    st.caption("Complete this before every trade to stay disciplined")

    # Load or use default
    saved = get_checklist_template(uid)
    items = saved.split("||") if saved else DEFAULT_CHECKLIST

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📋 Today's Checklist")
        all_checked = True
        checks = {}
        for i, item in enumerate(items):
            checks[i] = st.checkbox(item, key=f"chk_{i}")
            if not checks[i]:
                all_checked = False

        st.markdown("<br>", unsafe_allow_html=True)
        checked_count = sum(checks.values())
        total = len(items)
        st.progress(checked_count / total)
        st.markdown(f"**{checked_count}/{total}** items checked")

        if all_checked:
            st.success("🟢 All checks passed — You are ready to trade!")
        elif checked_count >= total * 0.8:
            st.warning("🟡 Almost ready — complete remaining checks")
        else:
            st.error("🔴 Not ready to trade yet — complete the checklist first!")

    with col2:
        st.markdown("### ⚙️ Customize Checklist")
        st.caption("Edit your checklist items (one per line)")
        custom_text = st.text_area(
            "Your checklist items",
            value=chr(10).join(items),
            height=300,
            key="custom_checklist"
        )
        if st.button("💾 Save Checklist", use_container_width=True, key="save_cl"):
            new_items = [x.strip() for x in custom_text.split(chr(10)) if x.strip()]
            save_checklist_template(uid, "||".join(new_items))
            st.success("Checklist saved!"); st.rerun()

        if st.button("↩️ Reset to Default", use_container_width=True, key="reset_cl"):
            save_checklist_template(uid, "||".join(DEFAULT_CHECKLIST))
            st.success("Reset done!"); st.rerun()

# ─────────────────────────────────────────────
# PDF REPORT
# ─────────────────────────────────────────────
def generate_pdf_report(df, username, account_info, month_label):
    """Generate HTML-based monthly report for download as PDF via browser print."""
    if df.empty:
        return None

    total = len(df)
    wins = (df["result"] == "Win").sum()
    losses = (df["result"] == "Loss").sum()
    wr = round(wins / total * 100, 1)
    total_pnl = round(df["pnl"].fillna(0).sum(), 2)
    avg_rr = round(df["rr"].dropna().mean(), 2) if not df["rr"].dropna().empty else 0
    gp = df[df["pnl"] > 0]["pnl"].sum()
    gl = abs(df[df["pnl"] < 0]["pnl"].sum())
    pf = round(gp / gl, 2) if gl else "∞"

    acc_name = account_info.get("account_name", "N/A") if account_info else "N/A"
    acc_size = account_info.get("account_size", 0) if account_info else 0
    currency = account_info.get("currency", "USD") if account_info else "USD"
    pnl_money = round(float(acc_size) * total_pnl / 100, 2) if acc_size else 0

    best_pair = df.groupby("pair")["pnl"].sum().idxmax() if not df.empty else "N/A"
    best_strat = df.groupby("strategy")["pnl"].sum().idxmax() if "strategy" in df.columns and df["strategy"].notna().any() else "N/A"

    # Trade rows
    trade_rows = ""
    for _, r in df.sort_values("trade_date", ascending=False).head(30).iterrows():
        color = "#22c55e" if r.get("result") == "Win" else ("#ef4444" if r.get("result") == "Loss" else "#f59e0b")
        pnl_val = r.get("pnl", 0) or 0
        trade_rows += f"""
        <tr>
            <td>{str(r.get("trade_date",""))[:10]}</td>
            <td><b>{r.get("pair","")}</b></td>
            <td>{r.get("direction","")}</td>
            <td>{r.get("strategy","")}</td>
            <td style="color:{color};font-weight:700">{r.get("result","")}</td>
            <td>{r.get("rr","") or "—"}</td>
            <td style="color:{color};font-weight:700">{pnl_val:+.2f}%</td>
            <td>{r.get("mood","")}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Trading Report — {username} — {month_label}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',sans-serif; background:#0a0e17; color:#f1f5f9; padding:40px; }}
  .header {{ text-align:center; border-bottom:2px solid #3b82f6; padding-bottom:24px; margin-bottom:32px; }}
  .header h1 {{ font-size:2rem; color:#60a5fa; }}
  .header p {{ color:#94a3b8; margin-top:8px; }}
  .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:32px; }}
  .metric {{ background:#111827; border:1px solid #2d3748; border-radius:12px; padding:16px; text-align:center; }}
  .metric .val {{ font-size:1.8rem; font-weight:800; color:#60a5fa; }}
  .metric .lbl {{ font-size:0.75rem; color:#94a3b8; margin-top:4px; text-transform:uppercase; letter-spacing:0.05em; }}
  .section {{ margin-bottom:28px; }}
  .section h2 {{ color:#60a5fa; font-size:1.1rem; margin-bottom:12px; border-left:3px solid #3b82f6; padding-left:10px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
  th {{ background:#1a2235; color:#94a3b8; padding:10px 8px; text-align:left; font-weight:600; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.05em; }}
  td {{ padding:8px; border-bottom:1px solid #2d3748; }}
  tr:hover td {{ background:#111827; }}
  .footer {{ text-align:center; color:#475569; font-size:0.8rem; margin-top:32px; padding-top:16px; border-top:1px solid #2d3748; }}
  .green {{ color:#22c55e; }} .red {{ color:#ef4444; }}
  @media print {{ body {{ background:white; color:black; }} .metric {{ background:#f8fafc; border-color:#e2e8f0; }} table th {{ background:#f1f5f9; color:#475569; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>📈 Trading Performance Report</h1>
  <p>Trader: <b>{username}</b> &nbsp;|&nbsp; Account: <b>{acc_name}</b> &nbsp;|&nbsp; Period: <b>{month_label}</b></p>
  <p style="margin-top:6px;color:#64748b;">Generated: {datetime.now().strftime("%d %b %Y %H:%M")}</p>
</div>

<div class="metrics">
  <div class="metric"><div class="val">{total}</div><div class="lbl">Total Trades</div></div>
  <div class="metric"><div class="val" style="color:{'#22c55e' if wr >= 50 else '#ef4444'}">{wr}%</div><div class="lbl">Win Rate</div></div>
  <div class="metric"><div class="val" style="color:{'#22c55e' if total_pnl >= 0 else '#ef4444'}">{total_pnl:+.2f}%</div><div class="lbl">Total PnL</div></div>
  <div class="metric"><div class="val" style="color:{'#22c55e' if pnl_money >= 0 else '#ef4444'}">{currency} {pnl_money:+,.2f}</div><div class="lbl">PnL in Money</div></div>
  <div class="metric"><div class="val">{wins}</div><div class="lbl">Wins</div></div>
  <div class="metric"><div class="val">{losses}</div><div class="lbl">Losses</div></div>
  <div class="metric"><div class="val">{pf}</div><div class="lbl">Profit Factor</div></div>
  <div class="metric"><div class="val">1:{avg_rr}</div><div class="lbl">Avg R:R</div></div>
</div>

<div class="section">
  <h2>🏆 Key Highlights</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Best Pair</td><td><b>{best_pair}</b></td></tr>
    <tr><td>Best Strategy</td><td><b>{best_strat}</b></td></tr>
    <tr><td>Account Size</td><td>{currency} {float(acc_size):,.0f}</td></tr>
    <tr><td>Report Period</td><td>{month_label}</td></tr>
  </table>
</div>

<div class="section">
  <h2>📋 Trade History (Last 30)</h2>
  <table>
    <tr><th>Date</th><th>Pair</th><th>Dir</th><th>Strategy</th><th>Result</th><th>R:R</th><th>PnL%</th><th>Mood</th></tr>
    {trade_rows}
  </table>
</div>

<div class="footer">Generated by Trading Journal &nbsp;•&nbsp; {datetime.now().strftime("%Y")}</div>
</body></html>"""
    return html

def show_pdf_export(df, username, account_info):
    st.markdown("## 📄 Export PDF Report")
    if df.empty:
        st.info("No trades to export.")
        return

    months_available = sorted(df["trade_date"].dt.to_period("M").unique(), reverse=True)
    month_labels = [str(m) for m in months_available]
    sel = st.selectbox("Select Month", month_labels, key="pdf_month")

    if st.button("📄 Generate Report", use_container_width=False, key="gen_pdf"):
        sel_period = pd.Period(sel, "M")
        df_month = df[df["trade_date"].dt.to_period("M") == sel_period]
        month_label = sel_period.strftime("%B %Y")
        html = generate_pdf_report(df_month, username, account_info, month_label)
        if html:
            st.download_button(
                label="⬇️ Download HTML Report (Open in browser → Print → Save as PDF)",
                data=html.encode("utf-8"),
                file_name=f"trading_report_{sel}.html",
                mime="text/html",
                key="download_pdf"
            )
            st.info("💡 Tip: Open downloaded file in Chrome → Ctrl+P → Save as PDF for best results!")
            with st.expander("👁️ Preview Report"):
                st.components.v1.html(html, height=600, scrolling=True)


# ─────────────────────────────────────────────
# MT5 CSV IMPORT
# ─────────────────────────────────────────────
def parse_mt5_csv(uploaded_file):
    try:
        raw = uploaded_file.read()
        for enc in ["utf-16","utf-8","latin-1"]:
            try:
                text = raw.decode(enc)
                break
            except:
                continue

        import io
        lines = text.splitlines()
        # Find header line
        header_idx = 0
        for i, line in enumerate(lines):
            low = line.lower()
            if any(x in low for x in ["symbol","ticket","pair","instrument"]):
                header_idx = i
                break

        data_text = chr(10).join(lines[header_idx:])
        df = pd.read_csv(io.StringIO(data_text), sep=None, engine="python", on_bad_lines="skip")
        df.columns = [str(c).strip().lower().replace(" ","_").replace("/","_") for c in df.columns]

        col_map = {}
        for c in df.columns:
            if any(x in c for x in ["symbol","pair","instrument"]): col_map["pair"] = c
            elif any(x in c for x in ["open_time","opentime","time","open_date","date"]): col_map["trade_date"] = c
            elif any(x in c for x in ["type","direction","cmd"]): col_map["direction"] = c
            elif any(x in c for x in ["open_price","openprice","price","entry"]): col_map["entry"] = c
            elif any(x in c for x in ["s_/_l","s/l","sl","stop_loss","stoploss"]): col_map["stop_loss"] = c
            elif any(x in c for x in ["t_/_p","t/p","tp","take_profit","takeprofit"]): col_map["take_profit"] = c
            elif any(x in c for x in ["profit","pnl","gain"]): col_map["pnl_raw"] = c
            elif any(x in c for x in ["volume","lots","size"]): col_map["lots"] = c
            elif any(x in c for x in ["comment","comments","notes"]): col_map["notes"] = c

        if "pair" not in col_map:
            return None, "Could not detect Symbol/Pair column. Please check your export."
        if "trade_date" not in col_map:
            return None, "Could not detect Date column."
        if "pnl_raw" not in col_map:
            return None, "Could not detect Profit column."

        trades = []
        for _, row in df.iterrows():
            try:
                pair = str(row[col_map["pair"]]).strip().upper()
                if not pair or pair in ["NAN","BALANCE","DEPOSIT","WITHDRAWAL","CREDIT","BONUS"]:
                    continue
                if len(pair) < 3:
                    continue

                raw_date = str(row[col_map["trade_date"]])
                try:
                    trade_date = pd.to_datetime(raw_date, dayfirst=False).date()
                except:
                    continue

                direction = "Buy"
                if "direction" in col_map:
                    d = str(row[col_map["direction"]]).lower()
                    direction = "Sell" if any(x in d for x in ["sell","1","short","s"]) else "Buy"

                entry = 0.0
                if "entry" in col_map:
                    try: entry = float(str(row[col_map["entry"]]).replace(",","."))
                    except: pass

                sl = 0.0
                if "stop_loss" in col_map:
                    try: sl = float(str(row[col_map["stop_loss"]]).replace(",","."))
                    except: pass

                tp = 0.0
                if "take_profit" in col_map:
                    try: tp = float(str(row[col_map["take_profit"]]).replace(",","."))
                    except: pass

                pnl_raw = 0.0
                try: pnl_raw = float(str(row[col_map["pnl_raw"]]).replace(",","."))
                except: pass

                notes_val = ""
                if "notes" in col_map:
                    notes_val = str(row[col_map["notes"]]) if str(row[col_map["notes"]]) != "nan" else ""

                result = "Win" if pnl_raw > 0 else ("Loss" if pnl_raw < 0 else "BE")

                rr = 0.0
                if entry > 0 and sl > 0 and tp > 0:
                    risk = abs(entry - sl)
                    reward = abs(tp - entry)
                    if risk > 0:
                        rr = round(reward / risk, 2)

                trades.append({
                    "pair": pair[:20],
                    "trade_date": str(trade_date),
                    "direction": direction,
                    "entry": entry,
                    "stop_loss": sl,
                    "take_profit": tp,
                    "pnl_raw": pnl_raw,
                    "result": result,
                    "notes": ("MT5 Import | " + notes_val).strip(" |"),
                    "session": "New York",
                    "strategy": "MT5 Import",
                    "mood": "Neutral",
                    "risk_pct": 1.0,
                    "rr": rr
                })
            except:
                continue

        if not trades:
            return None, "No valid trades found. Make sure to export only closed trades."
        return pd.DataFrame(trades), None

    except Exception as e:
        return None, f"Error reading file: {e}"


def show_mt5_import(uid, aid):
    st.markdown("## 📥 MT5 Trade Import")
    st.caption("Import your closed trades from MetaTrader 5")

    if not aid:
        st.warning("⚠️ Please select an account first from **💼 Accounts** page.")
        return

    with st.expander("📖 How to export from MT5 — Step by Step", expanded=True):
        st.markdown("""
**Step 1** — Open MetaTrader 5

**Step 2** — Bottom panel → Click **"History"** tab

**Step 3** — Right-click anywhere in the history → **"Report"**

**Step 4** — Choose date range → Click **"Open"**

**Step 5** — In the report window → **File → Save As**

**Step 6** — Save as **CSV** format → Upload below ⬇️

> ⚠️ Make sure "Deals" or "Closed Positions" is selected, not "Open Orders"
        """)

    uploaded = st.file_uploader("📁 Upload MT5 CSV / HTM File", type=["csv","htm","html","txt"], key="mt5_file")

    if not uploaded:
        return

    with st.spinner("Parsing MT5 file..."):
        df_mt5, err = parse_mt5_csv(uploaded)

    if err:
        st.error(f"❌ {err}")
        st.info("💡 Try: In MT5 History tab → Right click → Save as Report → Select CSV format")
        return

    st.success(f"✅ Found **{len(df_mt5)}** trades!")
    st.markdown("### Preview (first 15 trades):")

    preview_cols = ["trade_date","pair","direction","entry","stop_loss","take_profit","result","pnl_raw","rr"]
    available = [c for c in preview_cols if c in df_mt5.columns]
    st.dataframe(df_mt5[available].head(15), use_container_width=True)

    acc = get_account_info(aid)
    acc_size = float(acc.get("account_size", 10000)) if acc else 10000
    currency = acc.get("currency", "USD") if acc else "USD"

    total_money = round(df_mt5["pnl_raw"].sum(), 2)
    wins = (df_mt5["result"] == "Win").sum()
    losses = (df_mt5["result"] == "Loss").sum()
    wr = round(wins / len(df_mt5) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", len(df_mt5))
    c2.metric("Win Rate", f"{wr}%")
    c3.metric(f"Total PnL ({currency})", f"{total_money:+,.2f}")
    c4.metric("W / L", f"{wins} / {losses}")

    st.markdown("---")
    st.warning(f"⚠️ Importing **{len(df_mt5)}** trades into your account. Importing same file twice will create duplicates.")

    col_imp, col_cancel = st.columns(2)
    with col_imp:
        if st.button("📥 Import All Trades", use_container_width=True, key="btn_import_mt5"):
            progress_bar = st.progress(0, text="Importing trades...")
            sb = get_supabase()
            total = len(df_mt5)
            imported = 0
            failed = 0

            # Batch insert for speed
            batch = []
            for _, row in df_mt5.iterrows():
                try:
                    pnl_pct = round(float(row["pnl_raw"]) / acc_size * 100, 4) if acc_size > 0 else 0
                    batch.append({
                        "user_id": uid,
                        "account_id": aid,
                        "pair": row["pair"],
                        "trade_date": row["trade_date"],
                        "session": "New York",
                        "strategy": "MT5 Import",
                        "direction": row["direction"],
                        "entry": float(row.get("entry") or 0),
                        "stop_loss": float(row.get("stop_loss") or 0),
                        "take_profit": float(row.get("take_profit") or 0),
                        "risk_pct": 1.0,
                        "result": row["result"],
                        "rr": float(row.get("rr") or 0),
                        "pnl": pnl_pct,
                        "mood": "Neutral",
                        "notes": row.get("notes","MT5 Import")
                    })
                    imported += 1
                except:
                    failed += 1

                if len(batch) >= 50:
                    sb.table("trades").insert(batch).execute()
                    batch = []
                    progress_bar.progress(imported / total, text=f"Importing... {imported}/{total}")

            if batch:
                sb.table("trades").insert(batch).execute()

            progress_bar.progress(1.0, text="Done!")
            st.success(f"🎉 Imported **{imported}** trades successfully!" + (f" ({failed} skipped)" if failed else ""))
            st.balloons()
            st.rerun()

    with col_cancel:
        if st.button("❌ Cancel", use_container_width=True, key="btn_cancel_import"):
            st.rerun()


# ─────────────────────────────────────────────
# AI TRADE COACH
# ─────────────────────────────────────────────



# ─────────────────────────────────────────────
# TRADE REPLAY
# ─────────────────────────────────────────────
def show_trade_replay(df):
    st.markdown("## 🎬 Trade Replay")
    st.caption("Visualize your trades — Entry, Stop Loss, Take Profit on a chart")

    if df.empty:
        st.info("No trades yet. Log some trades first!")
        return

    dark = st.session_state.get("dark_mode", True)
    bg = "#0a0e17" if dark else "#f8fafc"
    text_c = "#f1f5f9" if dark else "#0f172a"
    grid_c = "#2d3748" if dark else "#e2e8f0"

    # Trade selector
    trade_labels = [
        f"#{int(r['id'])} — {str(r['trade_date'])[:10]} | {r['pair']} | {r['direction']} | {r['result']} | {r.get('pnl',0):+.2f}%"
        for _, r in df.head(100).iterrows()
        if r.get('entry') and r.get('stop_loss') and r.get('take_profit')
    ]

    if not trade_labels:
        st.warning("No trades with Entry/SL/TP data found. Make sure to fill these when logging trades.")
        return

    sel = st.selectbox("Select Trade to Replay", trade_labels, key="replay_sel")
    idx = trade_labels.index(sel)
    valid_df = df[(df['entry'].notna()) & (df['stop_loss'].notna()) & (df['take_profit'].notna())].head(100)
    row = valid_df.iloc[idx]

    entry = float(row['entry'])
    sl = float(row['stop_loss'])
    tp = float(row['take_profit'])
    direction = row.get('direction', 'Buy')
    result = row.get('result', '—')
    pair = row.get('pair', '—')
    rr = row.get('rr', 0) or 0
    pnl = row.get('pnl', 0) or 0
    mood = row.get('mood', '—')
    strategy = row.get('strategy', '—')

    # Colors
    entry_color = "#3b82f6"
    sl_color = "#ef4444"
    tp_color = "#22c55e"
    result_color = "#22c55e" if result == "Win" else ("#ef4444" if result == "Loss" else "#f59e0b")

    # Price range for chart
    prices = [entry, sl, tp]
    price_min = min(prices)
    price_max = max(prices)
    padding = (price_max - price_min) * 0.3
    y_min = price_min - padding
    y_max = price_max + padding

    # Build chart
    fig = go.Figure()

    # Background zones
    if direction == "Buy":
        # Profit zone (entry to TP) - green
        fig.add_hrect(y0=entry, y1=tp, fillcolor="rgba(34,197,94,0.08)", line_width=0)
        # Loss zone (SL to entry) - red
        fig.add_hrect(y0=sl, y1=entry, fillcolor="rgba(239,68,68,0.08)", line_width=0)
    else:
        # Profit zone (TP to entry) - green
        fig.add_hrect(y0=tp, y1=entry, fillcolor="rgba(34,197,94,0.08)", line_width=0)
        # Loss zone (entry to SL) - red
        fig.add_hrect(y0=entry, y1=sl, fillcolor="rgba(239,68,68,0.08)", line_width=0)

    # Horizontal lines
    fig.add_hline(y=entry, line_color=entry_color, line_width=2.5, line_dash="solid",
                  annotation_text=f"  ENTRY: {entry:.5f}", annotation_font_color=entry_color,
                  annotation_position="right")
    fig.add_hline(y=sl, line_color=sl_color, line_width=2.5, line_dash="dash",
                  annotation_text=f"  STOP LOSS: {sl:.5f}", annotation_font_color=sl_color,
                  annotation_position="right")
    fig.add_hline(y=tp, line_color=tp_color, line_width=2.5, line_dash="dash",
                  annotation_text=f"  TAKE PROFIT: {tp:.5f}", annotation_font_color=tp_color,
                  annotation_position="right")

    # Result marker
    hit_price = tp if result == "Win" else (sl if result == "Loss" else entry)
    fig.add_trace(go.Scatter(
        x=[0.5], y=[hit_price],
        mode="markers+text",
        marker=dict(size=18, color=result_color, symbol="star", line=dict(color="white", width=1)),
        text=[f" {result}!"],
        textfont=dict(color=result_color, size=14),
        textposition="middle right",
        showlegend=False
    ))

    # Direction arrow
    arrow_y0 = entry
    arrow_y1 = tp if direction == "Buy" else sl
    fig.add_annotation(
        x=0.5, y=arrow_y1,
        ax=0.5, ay=arrow_y0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor=entry_color
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_c),
        height=450,
        margin=dict(l=20, r=150, t=40, b=20),
        xaxis=dict(
            visible=False,
            range=[0, 1]
        ),
        yaxis=dict(
            gridcolor=grid_c,
            range=[y_min, y_max],
            tickformat=".5f"
        ),
        title=dict(
            text=f"{direction} {pair} — {result}",
            font=dict(color=result_color, size=18),
            x=0.02
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Trade stats below chart
    st.markdown("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pair", pair)
    c2.metric("Direction", f"{'📈' if direction == 'Buy' else '📉'} {direction}")
    c3.metric("Result", f"{'✅' if result == 'Win' else '❌' if result == 'Loss' else '⚖️'} {result}")
    c4.metric("R:R", f"1:{rr}")
    c5.metric("PnL", f"{pnl:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**Strategy:** {strategy}")
        st.markdown(f"**Mood:** {mood}")
    with d2:
        risk_pips = abs(entry - sl)
        reward_pips = abs(tp - entry)
        st.markdown(f"**Risk (pips):** {risk_pips:.5f}")
        st.markdown(f"**Reward (pips):** {reward_pips:.5f}")

    if row.get('notes'):
        st.markdown("**Notes:**")
        st.markdown(str(row['notes']))

# ─────────────────────────────────────────────
# ADMIN PAGE
# ─────────────────────────────────────────────
def show_admin(uid, username):
    st.markdown("## ⚙️ Admin Panel")
    if username != ADMIN_USERNAME:
        st.error("🚫 Access Denied."); return
    st.success(f"✅ Admin: **{username}**")
    users = get_all_users()
    st.markdown(f"### 👥 All Users ({len(users)})")
    for _, u in users.iterrows():
        df_t = load_trades(u["id"])
        is_self = u["username"] == username
        c1,c2 = st.columns([4,1])
        with c1:
            tag = " 👑 (You)" if is_self else ""
            st.markdown(f"**{u['username']}**{tag}")
            st.caption(f"🗓️ {u['created_at'][:10]}  |  📊 {len(df_t)} trades")
        with c2:
            if not is_self:
                if st.button("🗑️ Delete", key=f"adel_{u['id']}", use_container_width=True):
                    st.session_state[f"adel_confirm_{u['id']}"] = True
        if st.session_state.get(f"adel_confirm_{u['id']}"):
            st.warning(f"Delete **{u['username']}** + ALL data?")
            y,n = st.columns(2)
            with y:
                if st.button(f"✅ Yes", key=f"adel_yes_{u['id']}", use_container_width=True):
                    delete_user_completely(u["id"])
                    st.session_state.pop(f"adel_confirm_{u['id']}", None)
                    st.success("Deleted."); st.rerun()
            with n:
                if st.button("❌ No", key=f"adel_no_{u['id']}", use_container_width=True):
                    st.session_state.pop(f"adel_confirm_{u['id']}", None); st.rerun()
        st.divider()

    # ── Bulk delete all non-admin users ──
    st.markdown("---")
    st.markdown("### 🧹 Bulk Actions")
    if st.button("🗑️ Delete ALL Users (except yourself)", key="adel_all", use_container_width=False):
        st.session_state["confirm_adel_all"] = True

    if st.session_state.get("confirm_adel_all"):
        st.error("⚠️ This will delete ALL users and their data except your account. Cannot be undone!")
        y, n = st.columns(2)
        with y:
            if st.button("✅ Yes, Delete All", key="adel_all_yes", use_container_width=True):
                all_users = get_all_users()
                for _, u in all_users.iterrows():
                    if u["username"] != username:
                        delete_user_completely(u["id"])
                st.session_state.pop("confirm_adel_all", None)
                st.success("All other users deleted.")
                st.rerun()
        with n:
            if st.button("❌ Cancel", key="adel_all_no", use_container_width=True):
                st.session_state.pop("confirm_adel_all", None)
                st.rerun()

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    apply_theme()

    # Remember Me auto-login
    if "user_id" not in st.session_state:
        # Try query param first (from localStorage redirect)
        try:
            token = st.query_params.get("tj_token")
            if not token:
                token = st.query_params.get("session")
            if token:
                sess = get_session(token)
                if sess:
                    st.session_state.update({
                        "user_id": sess[0],
                        "username": sess[1],
                        "active_account_id": None,
                        "session_token": token
                    })
        except:
            pass

    # If still not logged in, try localStorage via JS bridge
    if "user_id" not in st.session_state:
        # Read localStorage and redirect with token in URL
        st.components.v1.html("""
        <script>
        (function() {
            var token = localStorage.getItem('tj_token');
            if (token) {
                var url = new URL(window.parent.location.href);
                if (!url.searchParams.get('tj_token')) {
                    url.searchParams.set('tj_token', token);
                    window.parent.location.replace(url.toString());
                }
            }
        })();
        </script>
        """, height=0)

    if "user_id" not in st.session_state:
        page_login()
        return

    uid = st.session_state["user_id"]
    username = st.session_state["username"]
    aid = st.session_state.get("active_account_id")
    acc_name = st.session_state.get("active_account_name","No Account Selected")

    render_navbar(username, acc_name)

    # Load trades + filter in sidebar
    df_all = load_trades(uid, aid)
    df = sidebar_filters(df_all)

    # Account info for daily loss limit
    account_info = get_account_info(aid) if aid else None

    # ── Sidebar — grouped navigation ──
    dark = st.session_state.get("dark_mode", True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🛠️ Tools")
    sb_tools = [
        ("🎯 Goals Tracker",      "goals"),
        ("✅ Pre-Trade Checklist", "checklist"),
        ("🎬 Trade Replay",       "trade_replay"),
    ]
    for label, pg in sb_tools:
        if st.sidebar.button(label, use_container_width=True, key=f"sb_{pg}"):
            st.session_state["page"] = pg; st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📋 Reports & Import")
    sb_reports = [
        ("📝 Weekly Review", "weekly_review"),
        ("📄 PDF Export",    "pdf_export"),
        ("📥 MT5 Import",    "mt5_import"),
    ]
    for label, pg in sb_reports:
        if st.sidebar.button(label, use_container_width=True, key=f"sb_{pg}"):
            st.session_state["page"] = pg; st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚙️ Settings")

    # Theme toggle
    theme_label = "☀️ Light Mode" if dark else "🌙 Dark Mode"
    if st.sidebar.button(theme_label, use_container_width=True, key="sb_theme"):
        st.session_state["dark_mode"] = not dark; st.rerun()

    # Admin
    if username == ADMIN_USERNAME:
        if st.sidebar.button("⚙️ Admin Panel", use_container_width=True, key="sb_admin"):
            st.session_state["page"] = "admin"; st.rerun()

    # Logout
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sb_logout"):
        token = st.session_state.get("session_token") or st.query_params.get("tj_token") or st.query_params.get("session")
        delete_session(token)
        st.components.v1.html("""
        <script>
        localStorage.removeItem('tj_token');
        var url = new URL(window.parent.location.href);
        url.searchParams.delete('tj_token');
        url.searchParams.delete('session');
        window.parent.location.replace(url.toString());
        </script>
        """, height=0)
        st.session_state.clear()


    if "page" not in st.session_state:
        st.session_state["page"] = "dashboard"

    page = st.session_state.get("page","dashboard")

    if page == "dashboard":        show_dashboard(df, account_info)
    elif page == "new_trade":      show_trade_form(uid, aid)
    elif page == "trade_log":      show_trade_log(df, uid)
    elif page == "accounts":       show_accounts(uid)
    elif page == "leaderboard":    show_leaderboard()
    elif page == "weekly_review":  show_weekly_review(uid)
    elif page == "goals":          show_goals(uid, df)
    elif page == "checklist":      show_checklist(uid)
    elif page == "pdf_export":     show_pdf_export(df, username, account_info)
    elif page == "mt5_import":     show_mt5_import(uid, aid)
    elif page == "trade_replay":   show_trade_replay(df)
    elif page == "admin":          show_admin(uid, username)

if __name__ == "__main__":
    main()