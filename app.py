"""WaterBuddy: your daily hydration companion (Streamlit, liquid-glass UI)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="WaterBuddy",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ───────────────────────── Constants ─────────────────────────
TZ = ZoneInfo("Asia/Kolkata")
RING_R = 90
RING_C = 2 * 3.14159265 * RING_R

AGE_GOALS = {
    "Children (4 to 8)": 1200,
    "Teens (9 to 13)": 1700,
    "Adults (14 to 64)": 2250,
    "Seniors (65+)": 1850,
}
AGE_AVATAR = {
    "Children (4 to 8)": "🧒",
    "Teens (9 to 13)": "🧑‍🎓",
    "Adults (14 to 64)": "🧑",
    "Seniors (65+)": "🧓",
}
QUICK_POURS = (150, 250, 350, 500)
MILESTONES = (25, 50, 75, 100)
MOMENT_TAGS = ("Sip", "Morning", "Study", "Workout")

# ───────────────────────── State & callbacks ─────────────────────────
DEFAULTS = {
    "age_group": "Adults (14 to 64)",
    "daily_goal": AGE_GOALS["Adults (14 to 64)"],
    "bottle_ml": 750,
    "selected_tag": "Sip",
    "sound_enabled": True,
    "entries": [],  # list of {"ml": int, "time": "03:00 PM", "tag": "Study"}
    "typed_amount": 0,
    "show_reset_confirm": False,
    "celebrated_milestones": [],
    "active_flower_milestone": None,
    "sound_trigger_id": 0,
    "dismissed_milestone": None,
}
for _k, _v in DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = list(_v) if isinstance(_v, list) else _v


def set_goal_from_age():
    st.session_state.daily_goal = AGE_GOALS[st.session_state.age_group]
    _sync_milestones()


def _sync_milestones():
    goal_val = max(1, int(st.session_state.daily_goal))
    total_val = sum(e["ml"] for e in st.session_state.entries)
    pct = (total_val / goal_val) * 100

    st.session_state.celebrated_milestones = [
        m for m in st.session_state.celebrated_milestones if pct >= m
    ]
    if (
        st.session_state.dismissed_milestone is not None
        and pct < st.session_state.dismissed_milestone
    ):
        st.session_state.dismissed_milestone = None

    newly_reached = [
        m for m in MILESTONES if pct >= m and m not in st.session_state.celebrated_milestones
    ]
    if newly_reached:
        highest = max(newly_reached)
        st.session_state.celebrated_milestones.extend(newly_reached)
        if highest != st.session_state.dismissed_milestone:
            st.session_state.active_flower_milestone = highest
            if st.session_state.sound_enabled:
                st.session_state.sound_trigger_id += 1
    elif (
        st.session_state.active_flower_milestone is not None
        and pct < st.session_state.active_flower_milestone
    ):
        st.session_state.active_flower_milestone = None


def add_water(amount, tag=None):
    amount = int(amount or 0)
    if amount > 0:
        chosen_tag = tag or st.session_state.get("selected_tag", "Sip")
        st.session_state.entries.append(
            {
                "ml": amount,
                "time": datetime.now(TZ).strftime("%I:%M %p"),
                "tag": chosen_tag,
            }
        )
        _sync_milestones()


def add_typed_water():
    add_water(st.session_state.typed_amount)
    st.session_state.typed_amount = 0


def undo_last():
    if st.session_state.entries:
        st.session_state.entries.pop()
        _sync_milestones()


def remove_entry(index):
    if 0 <= index < len(st.session_state.entries):
        st.session_state.entries.pop(index)
        _sync_milestones()


def dismiss_flower():
    st.session_state.dismissed_milestone = st.session_state.active_flower_milestone
    st.session_state.active_flower_milestone = None


def ask_new_day():
    st.session_state.show_reset_confirm = True


def cancel_new_day():
    st.session_state.show_reset_confirm = False


def reset_new_day():
    st.session_state.entries = []
    st.session_state.show_reset_confirm = False
    st.session_state.celebrated_milestones = []
    st.session_state.active_flower_milestone = None
    st.session_state.dismissed_milestone = None


# ───────────────────────── Styling ─────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root{
  --ink:#222052; --ink-soft:#5b5b8e; --accent:#6c5ce7; --accent-2:#8d7ff5;
  --sky:#a9d2ea; --lav:#d6d0f8;
  --glass:rgba(255,255,255,.38); --glass-strong:rgba(255,255,255,.62);
  --edge:rgba(255,255,255,.78);
  --shadow:0 18px 44px rgba(78,66,164,.14);
  color-scheme: light;
}

/* ── base + animated liquid backdrop ── */
html, body, .stApp, [data-testid="stAppViewContainer"]{
  color-scheme: light !important; color: var(--ink);
  background: linear-gradient(155deg,#c3e3f2 0%,#dcd5fa 52%,#c5dcf4 100%) fixed !important;
}
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4{
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
.stApp::before, .stApp::after{
  content:""; position:fixed; z-index:0; pointer-events:none; border-radius:50%;
  filter:blur(64px); opacity:.72;
}
.stApp::before{ width:46vmax; height:46vmax; left:-14vmax; top:-12vmax;
  background:radial-gradient(circle,#9e90ff 0%,transparent 68%); animation:drift 22s ease-in-out infinite alternate; }
.stApp::after{ width:42vmax; height:42vmax; right:-12vmax; bottom:-14vmax;
  background:radial-gradient(circle,#6ec4ea 0%,transparent 68%); animation:drift 26s ease-in-out infinite alternate-reverse; }
@keyframes drift{ to{ transform:translate(6vmax,4vmax) scale(1.08); } }

[data-testid="stHeader"]{ background:transparent !important; }
#MainMenu, footer, [data-testid="stDecoration"]{ display:none !important; }
[data-testid="stMainBlockContainer"], .block-container{
  position:relative; z-index:1; max-width:1120px; margin:0 auto;
  padding:clamp(.85rem,2.5vw,2rem) clamp(.85rem,3vw,2rem) 4rem;
}

/* ── liquid glass surfaces ── */
.wb-glass, [data-testid="stVerticalBlockBorderWrapper"]{
  position:relative; overflow:hidden;
  background:linear-gradient(135deg,rgba(255,255,255,.58),rgba(255,255,255,.26)) !important;
  -webkit-backdrop-filter:blur(26px) saturate(175%); backdrop-filter:blur(26px) saturate(175%);
  border:1px solid var(--edge) !important; border-radius:28px !important;
  box-shadow:inset 0 1.5px 0 rgba(255,255,255,.95), inset 0 -1px 0 rgba(255,255,255,.28), var(--shadow);
}
.wb-glass::before, [data-testid="stVerticalBlockBorderWrapper"]::before{
  content:""; position:absolute; inset:0; pointer-events:none; border-radius:inherit;
  background:radial-gradient(125% 75% at 10% -12%,rgba(255,255,255,.62),transparent 56%);
}
[data-testid="stVerticalBlockBorderWrapper"] > div{ position:relative; }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:20px !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.92);
}

/* ── header ── */
.wb-hero{ display:flex; align-items:center; gap:clamp(12px,2.4vw,22px); padding:clamp(18px,3vw,28px); margin-bottom:1.05rem; }
.wb-avatar{ flex:0 0 auto; width:clamp(56px,9vw,74px); aspect-ratio:1; display:grid; place-items:center;
  font-size:clamp(28px,5vw,38px); border-radius:50%;
  background:linear-gradient(145deg,#ffffff,#e6e0fc);
  box-shadow:inset 0 -3px 8px rgba(108,92,231,.18),0 10px 22px rgba(108,92,231,.24); }
.wb-hello{ color:var(--ink-soft); font-size:.88rem; font-weight:600; letter-spacing:.01em; }
.wb-brand{
  font-family:'Fraunces',Georgia,serif !important;
  font-size:clamp(1.65rem,4.2vw,2.3rem); font-weight:800; letter-spacing:-.025em; line-height:1.08;
  color:var(--ink);
}
.wb-tag{ color:var(--ink-soft); font-size:.9rem; margin-top:3px; font-weight:500; }
.wb-pills{ margin-left:auto; display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
.wb-pill{ padding:9px 14px; border-radius:18px; background:var(--glass-strong); border:1px solid var(--edge);
  text-align:center; min-width:108px; box-shadow:inset 0 1px 0 #fff; }
.wb-pill b{ display:block; font-size:1.02rem; font-weight:800; }
.wb-pill small{ color:var(--ink-soft); font-size:.7rem; font-weight:600; }

/* ── section titles ── */
.wb-h{
  font-family:'Fraunces',Georgia,serif !important;
  font-size:1.18rem; font-weight:700; letter-spacing:-.015em; margin:.1rem 0 .15rem;
}
.wb-sub{ color:var(--ink-soft); font-size:.88rem; margin-bottom:.75rem; }

/* ── progress ring with liquid wave ── */
.wb-ring{ position:relative; width:min(100%,292px); margin:.35rem auto .55rem; aspect-ratio:1; }
.wb-ring svg{ width:100%; height:100%; display:block; overflow:visible; }
.wb-track{ fill:none; stroke:rgba(255,255,255,.72); stroke-width:12; }
.wb-arc{ fill:none; stroke:url(#wbArc); stroke-width:12; stroke-linecap:round;
  transition:stroke-dasharray .9s cubic-bezier(.16,1,.3,1); filter:drop-shadow(0 4px 8px rgba(108,92,231,.32)); }
.wb-lvl{ transition:transform 1s cubic-bezier(.16,1,.3,1); }
.wb-w1{ animation:slide 7s linear infinite; }
.wb-w2{ animation:slide 11s linear infinite reverse; }
@keyframes slide{ to{ transform:translateX(-100px); } }
.wb-ring-text{ position:absolute; inset:0; display:grid; place-content:center; text-align:center; pointer-events:none; }
.wb-big{ font-size:clamp(1.7rem,6vw,2.3rem); font-weight:800; letter-spacing:-.03em; line-height:1; }
.wb-big small{ font-size:.5em; font-weight:700; color:var(--ink-soft); }
.wb-liters{ font-size:.98rem; font-weight:800; color:var(--accent); margin-top:4px; }
.wb-of{ color:var(--ink-soft); font-size:.8rem; font-weight:600; margin-top:4px; }

.wb-left{ display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:6px; padding:12px 16px; border-radius:18px;
  background:var(--glass-strong); border:1px solid var(--edge); box-shadow:inset 0 1px 0 #fff; text-align:center; }
.wb-left b{ color:var(--accent); font-size:1.05rem; font-weight:800; }
.wb-left span{ color:var(--ink-soft); font-size:.88rem; }

.wb-meta-row{ display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap; margin-top:10px; }
.wb-chip{ font-size:.77rem; font-weight:700; color:var(--ink); background:rgba(255,255,255,.64);
  border:1px solid var(--edge); padding:6px 12px; border-radius:999px; }

.wb-milestones-strip{
  display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-top:10px;
}
.wb-ms-badge{
  text-align:center; padding:7px 6px; border-radius:14px; font-size:.76rem; font-weight:800;
  background:rgba(255,255,255,.38); border:1px solid rgba(255,255,255,.65); color:var(--ink-soft);
}
.wb-ms-badge.is-done{
  background:linear-gradient(135deg,rgba(108,92,231,.22),rgba(111,195,232,.28));
  border-color:rgba(255,255,255,.95); color:var(--ink);
  box-shadow:inset 0 1px 0 #fff;
}

.wb-msg{ margin-top:10px; padding:13px 16px; border-radius:18px; font-weight:700; line-height:1.42;
  background:linear-gradient(135deg,rgba(108,92,231,.16),rgba(111,195,232,.2)); border:1px solid var(--edge); }

/* ── boxless single big 3D red rose in center (no text, fades smoothly after 5s) ── */
.wb-rose-only-wrap{
  position:fixed;
  top:50%;
  left:50%;
  transform:translate(-50%, -50%);
  z-index:999;
  pointer-events:none;
  display:grid;
  place-items:center;
  perspective:1100px;
  animation:roseLifetime5s 5.6s cubic-bezier(.22,1,.36,1) forwards;
}
@keyframes roseLifetime5s{
  0%{ opacity:1; transform:translate(-50%, -50%) scale(1); }
  84%{ opacity:1; transform:translate(-50%, -50%) scale(1); }
  100%{ opacity:0; transform:translate(-50%, -56%) scale(.86); visibility:hidden; }
}

.wb-rose-3d{
  width:clamp(190px,36vw,268px);
  height:clamp(190px,36vw,268px);
  overflow:visible;
  transform-origin:50% 58%;
  transform-style:preserve-3d;
  filter:drop-shadow(0 22px 38px rgba(159,18,57,.42));
  animation:
    roseUltraSmoothBloom 1.35s cubic-bezier(.16,1,.3,1) both,
    roseUltraSmoothBreathe 4.2s ease-in-out 1.35s infinite alternate;
}
@keyframes roseUltraSmoothBloom{
  0%{ opacity:0; transform:scale(.12) rotateY(-48deg) rotateZ(-14deg); }
  65%{ opacity:1; transform:scale(1.07) rotateY(6deg) rotateZ(2deg); }
  100%{ opacity:1; transform:scale(1) rotateY(0deg) rotateZ(0deg); }
}
@keyframes roseUltraSmoothBreathe{
  0%{ transform:translateY(0px) rotateY(-8deg) rotateZ(-1.5deg) scale(1); }
  100%{ transform:translateY(-10px) rotateY(9deg) rotateZ(2deg) scale(1.03); }
}

/* ── slightly bigger multi-colored stars falling smoothly across screen ── */
.wb-fall-star{
  position:fixed;
  top:-64px;
  z-index:998;
  pointer-events:none;
  filter:drop-shadow(0 6px 12px rgba(84,72,170,.22));
}
.wb-fall-star svg{ width:100%; height:100%; display:block; }

.wb-f1{ left:8%;  width:42px; height:42px; animation:fallSmoothA 4.8s cubic-bezier(.25,.8,.25,1) 0.05s forwards; }
.wb-f2{ left:21%; width:38px; height:38px; animation:fallSmoothB 5.1s cubic-bezier(.25,.8,.25,1) 0.28s forwards; }
.wb-f3{ left:34%; width:46px; height:46px; animation:fallSmoothA 4.9s cubic-bezier(.25,.8,.25,1) 0.14s forwards; }
.wb-f4{ left:48%; width:40px; height:40px; animation:fallSmoothB 5.2s cubic-bezier(.25,.8,.25,1) 0.42s forwards; }
.wb-f5{ left:62%; width:44px; height:44px; animation:fallSmoothA 4.7s cubic-bezier(.25,.8,.25,1) 0.20s forwards; }
.wb-f6{ left:75%; width:39px; height:39px; animation:fallSmoothB 5.0s cubic-bezier(.25,.8,.25,1) 0.36s forwards; }
.wb-f7{ left:87%; width:45px; height:45px; animation:fallSmoothA 4.85s cubic-bezier(.25,.8,.25,1) 0.10s forwards; }
.wb-f8{ left:14%; width:41px; height:41px; animation:fallSmoothB 5.3s cubic-bezier(.25,.8,.25,1) 0.55s forwards; }
.wb-f9{ left:54%; width:37px; height:37px; animation:fallSmoothA 4.95s cubic-bezier(.25,.8,.25,1) 0.65s forwards; }
.wb-f10{ left:81%; width:43px; height:43px; animation:fallSmoothB 5.15s cubic-bezier(.25,.8,.25,1) 0.48s forwards; }

@keyframes fallSmoothA{
  0%{ opacity:0; transform:translate3d(0, -20px, 0) rotate(0deg) scale(.75); }
  12%{ opacity:1; }
  50%{ transform:translate3d(26px, 48vh, 0) rotate(170deg) scale(1.06); }
  85%{ opacity:.92; }
  100%{ opacity:0; transform:translate3d(-14px, 102vh, 0) rotate(340deg) scale(.9); visibility:hidden; }
}
@keyframes fallSmoothB{
  0%{ opacity:0; transform:translate3d(0, -20px, 0) rotate(0deg) scale(.78); }
  12%{ opacity:1; }
  50%{ transform:translate3d(-28px, 50vh, 0) rotate(-185deg) scale(1.08); }
  85%{ opacity:.92; }
  100%{ opacity:0; transform:translate3d(18px, 102vh, 0) rotate(-360deg) scale(.9); visibility:hidden; }
}

/* ── records ── */
.wb-rec{ display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:18px;
  background:var(--glass-strong); border:1px solid var(--edge); box-shadow:inset 0 1px 0 #fff; }
.wb-rec-ic{ width:38px; height:38px; border-radius:13px; display:grid; place-items:center; font-size:1.1rem;
  background:linear-gradient(145deg,#e7e2fd,#cfe7f6); flex:0 0 auto; }
.wb-rec-t{ font-weight:700; font-size:.95rem; }
.wb-rec-s{ color:var(--ink-soft); font-size:.78rem; font-weight:600; }
.wb-rec-ml{ margin-left:auto; font-weight:800; white-space:nowrap; text-align:right; }
.wb-rec-ml small{ display:block; font-size:.72rem; font-weight:700; color:var(--ink-soft); }
.wb-empty{ text-align:center; color:var(--ink-soft); padding:1.4rem .5rem; font-weight:600; }
.wb-stat{ text-align:center; padding:12px 8px; border-radius:18px; background:var(--glass-strong);
  border:1px solid var(--edge); box-shadow:inset 0 1px 0 #fff; }
.wb-stat b{ display:block; font-size:1.15rem; font-weight:800; }
.wb-stat span{ display:block; font-size:.78rem; font-weight:700; color:var(--accent); margin-top:1px; }
.wb-stat small{ color:var(--ink-soft); font-weight:600; font-size:.74rem; }
.wb-stats{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:12px; }

/* ── tabs as floating glass pill ── */
[data-baseweb="tab-list"]{ gap:4px !important; padding:5px; width:fit-content; max-width:100%; margin:0 auto 1rem;
  border-radius:22px; background:var(--glass); border:1px solid var(--edge);
  -webkit-backdrop-filter:blur(20px); backdrop-filter:blur(20px); box-shadow:inset 0 1px 0 #fff,var(--shadow); }
[data-baseweb="tab"]{ border-radius:17px !important; padding:9px 22px !important; height:auto !important; background:transparent !important; }
[data-baseweb="tab"] p{ font-weight:700 !important; color:var(--ink-soft) !important; }
[data-baseweb="tab"][aria-selected="true"]{ background:linear-gradient(135deg,var(--accent),var(--accent-2)) !important; box-shadow:0 6px 16px rgba(108,92,231,.4); }
[data-baseweb="tab"][aria-selected="true"] p{ color:#fff !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"]{ display:none !important; }
[data-testid="stTabs"]{ display:block; }

/* ── buttons ── */
.stApp [data-testid^="stBaseButton"]{
  border-radius:16px; min-height:46px; font-weight:700; color:var(--ink) !important;
  background:var(--glass-strong) !important; border:1px solid var(--edge) !important;
  box-shadow:inset 0 1px 0 #fff,0 6px 14px rgba(84,72,170,.1);
  transition:transform .15s ease,box-shadow .15s ease,background .15s ease;
}
.stApp [data-testid^="stBaseButton"] p{ color:inherit !important; font-weight:700; }
.stApp [data-testid^="stBaseButton"]:hover{ transform:translateY(-2px); background:rgba(255,255,255,.85) !important; box-shadow:inset 0 1px 0 #fff,0 10px 20px rgba(84,72,170,.18); }
.stApp [data-testid^="stBaseButton"]:active{ transform:scale(.97); }
.stApp [data-testid="stBaseButton-primary"]{
  color:#fff !important; border-color:rgba(255,255,255,.4) !important;
  background:linear-gradient(135deg,var(--accent),var(--accent-2)) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 10px 22px rgba(108,92,231,.38);
}
.stApp [data-testid="stBaseButton-primary"]:hover{ background:linear-gradient(135deg,#5d4de0,#7d6ff0) !important; }
.stApp [data-testid="stBaseButton-primary"] p{ color:#fff !important; }
.stApp button:focus-visible, .stApp input:focus-visible{ outline:3px solid rgba(108,92,231,.55) !important; outline-offset:2px; }

/* ── inputs & pills ── */
.stApp label, .stApp [data-testid="stWidgetLabel"] p{ color:var(--ink) !important; font-weight:700 !important; }
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"]{
  background:rgba(255,255,255,.72) !important; border-radius:16px !important; border-color:var(--edge) !important;
}
[data-baseweb="select"] *, [data-baseweb="input"] input{ color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] ul{ background:rgba(255,255,255,.94) !important; border-radius:16px !important; }
[data-testid="stNumberInput"] button{ min-height:0 !important; box-shadow:none !important; }

/* ── responsive: quick pours 2×2 on phones, 4×1 on wider screens ── */
.st-key-quick [data-testid="stHorizontalBlock"]{ flex-wrap:wrap !important; gap:.6rem !important; }
.st-key-quick [data-testid="stColumn"]{ flex:1 1 calc(50% - .6rem) !important; min-width:calc(50% - .6rem) !important; width:auto !important; }
@media (min-width:480px){ .st-key-quick [data-testid="stColumn"]{ flex-basis:calc(25% - .6rem) !important; min-width:calc(25% - .6rem) !important; } }

/* record rows keep the delete button inline on every screen */
.st-key-records [data-testid="stHorizontalBlock"]{ flex-wrap:nowrap !important; gap:.5rem !important; align-items:center; margin-bottom:.45rem; }
.st-key-records [data-testid="stColumn"]{ min-width:0 !important; }
.st-key-records [data-testid="stColumn"]:first-child{ flex:1 1 auto !important; width:auto !important; }
.st-key-records [data-testid="stColumn"]:last-child{ flex:0 0 50px !important; width:50px !important; }

@media (max-width:760px){
  .wb-hero{ flex-wrap:wrap; } .wb-pills{ margin-left:0; width:100%; justify-content:stretch; } .wb-pill{ flex:1; }
  [data-baseweb="tab"]{ padding:8px 16px !important; }
}
@media (max-height:520px) and (orientation:landscape){
  .wb-ring{ width:min(100%,200px); } .wb-hero{ padding:12px 16px; } .wb-tag{ display:none; }
}
@media (min-width:761px) and (max-width:1024px){ .wb-pill{ min-width:84px; } }

@media (prefers-reduced-motion:reduce){
  .stApp::before,.stApp::after,.wb-w1,.wb-w2,.wb-rose-only-wrap,.wb-rose-3d,.wb-fall-star{ animation:none !important; }
  .wb-arc,.wb-lvl,.stApp [data-testid^="stBaseButton"]{ transition:none !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ───────────────────────── Helpers ─────────────────────────
def html(markup: str) -> None:
    """Render HTML without Markdown turning indented lines into code blocks."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def fmt_liters(ml: float) -> str:
    """Format milliliters into clean liters (e.g., 2250 -> '2.25 L', 500 -> '0.5 L')."""
    liters = f"{ml / 1000:.2f}".rstrip("0").rstrip(".")
    return f"{liters} L"


def feedback(percent: float) -> str:
    if percent >= 100:
        return "Goal achieved today — calm, steady hydration from start to finish. ✨"
    if percent >= 75:
        return "Past 75% — you're in the home stretch for today's target. 🌊"
    if percent >= 50:
        return "Halfway there — your hydration curve is building nicely. 😊"
    return "Every glass counts — steady sips keep focus and energy smooth. 💙"


def pace_status(now_dt: datetime, current_pct: float) -> str:
    """Gentle daytime pace estimate across waking hours (7 AM to 10 PM)."""
    minutes_since_wake = max(0, min(15 * 60, (now_dt.hour * 60 + now_dt.minute) - 7 * 60))
    expected_pct = (minutes_since_wake / (15 * 60)) * 100
    if current_pct >= 100:
        return "✨ Goal complete"
    if current_pct + 8 >= expected_pct:
        return "🌿 On pace"
    return "💧 Gentle catch-up"


def play_water_then_congrats(trigger_id: int) -> None:
    """Play a water splash/droplet sound first, followed by 'Congratulations!'."""
    if trigger_id <= 0:
        return
    components.html(
        f"""
        <!-- trigger: {trigger_id} -->
        <script>
        (function() {{
          try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            if (ctx.state === "suspended") ctx.resume();

            const now = ctx.currentTime;

            // 1) Water splash (filtered noise swell) + rising water droplets
            const dur = 0.55;
            const bufLen = Math.floor(ctx.sampleRate * dur);
            const buf = ctx.createBuffer(1, bufLen, ctx.sampleRate);
            const ch = buf.getChannelData(0);
            for (let i = 0; i < bufLen; i++) {{
              const t = i / bufLen;
              const env = Math.sin(Math.min(1, t * 2.2) * Math.PI) * Math.exp(-t * 2.2);
              ch[i] = (Math.random() * 2 - 1) * env;
            }}
            const noise = ctx.createBufferSource();
            noise.buffer = buf;

            const bp = ctx.createBiquadFilter();
            bp.type = "bandpass";
            bp.frequency.setValueAtTime(520, now);
            bp.frequency.exponentialRampToValueAtTime(1650, now + 0.32);
            bp.frequency.exponentialRampToValueAtTime(750, now + dur);
            bp.Q.setValueAtTime(2.4, now);

            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.001, now);
            nGain.gain.linearRampToValueAtTime(0.35, now + 0.06);
            nGain.gain.exponentialRampToValueAtTime(0.001, now + dur);

            noise.connect(bp);
            bp.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(now);

            // Cute water "bloop" droplets
            [0.05, 0.17, 0.30].forEach((offset, idx) => {{
              const dOsc = ctx.createOscillator();
              const dGain = ctx.createGain();
              const baseF = 360 + idx * 140;
              dOsc.type = "sine";
              dOsc.frequency.setValueAtTime(baseF, now + offset);
              dOsc.frequency.exponentialRampToValueAtTime(baseF * 1.9, now + offset + 0.11);

              dGain.gain.setValueAtTime(0.001, now + offset);
              dGain.gain.linearRampToValueAtTime(0.16, now + offset + 0.015);
              dGain.gain.exponentialRampToValueAtTime(0.0008, now + offset + 0.13);

              dOsc.connect(dGain);
              dGain.connect(ctx.destination);
              dOsc.start(now + offset);
              dOsc.stop(now + offset + 0.14);
            }});

            // 2) After the water sound finishes (~0.62s), say "Congratulations!"
            setTimeout(() => {{
              try {{
                if ("speechSynthesis" in window) {{
                  window.speechSynthesis.cancel();
                  const utter = new SpeechSynthesisUtterance("Congratulations!");
                  utter.rate = 1.02;
                  utter.pitch = 1.15;
                  utter.volume = 1.0;
                  window.speechSynthesis.speak(utter);
                }} else {{
                  const t0 = ctx.currentTime;
                  [587.33, 783.99, 1046.5].forEach((f, i) => {{
                    const o = ctx.createOscillator();
                    const g = ctx.createGain();
                    o.type = "triangle";
                    o.frequency.setValueAtTime(f, t0 + i * 0.08);
                    g.gain.setValueAtTime(0.001, t0 + i * 0.08);
                    g.gain.linearRampToValueAtTime(0.15, t0 + i * 0.08 + 0.02);
                    g.gain.exponentialRampToValueAtTime(0.0008, t0 + i * 0.08 + 0.35);
                    o.connect(g);
                    g.connect(ctx.destination);
                    o.start(t0 + i * 0.08);
                    o.stop(t0 + i * 0.08 + 0.36);
                  }});
                }}
              }} catch (err) {{}}
            }}, 620);
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def _star_svg(gid: str, fill_top: str, fill_bottom: str) -> str:
    return f"""
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{fill_top}"/>
          <stop offset="100%" stop-color="{fill_bottom}"/>
        </linearGradient>
      </defs>
      <polygon points="24,3 29.8,16.4 44.3,17.8 33.3,27.3 36.6,41.6 24,34 11.4,41.6 14.7,27.3 3.7,17.8 18.2,16.4"
               fill="url(#{gid})" stroke="#ffffff" stroke-width="1.6" stroke-linejoin="round"/>
      <polygon points="24,3 29.8,16.4 24,20.5" fill="#ffffff" opacity=".48"/>
    </svg>
    """


def single_rose_and_falling_stars_html() -> str:
    return f"""
    <div class="wb-fall-star wb-f1">{_star_svg("fs1", "#ffe066", "#fb8500")}</div>
    <div class="wb-fall-star wb-f2">{_star_svg("fs2", "#ff8fab", "#e63946")}</div>
    <div class="wb-fall-star wb-f3">{_star_svg("fs3", "#90e0ef", "#0077b6")}</div>
    <div class="wb-fall-star wb-f4">{_star_svg("fs4", "#c77dff", "#7209b7")}</div>
    <div class="wb-fall-star wb-f5">{_star_svg("fs5", "#80ed99", "#2b9348")}</div>
    <div class="wb-fall-star wb-f6">{_star_svg("fs6", "#ffd166", "#ef476f")}</div>
    <div class="wb-fall-star wb-f7">{_star_svg("fs7", "#a8dadc", "#457b9d")}</div>
    <div class="wb-fall-star wb-f8">{_star_svg("fs8", "#f4a261", "#e76f51")}</div>
    <div class="wb-fall-star wb-f9">{_star_svg("fs9", "#b8f2e6", "#0096c7")}</div>
    <div class="wb-fall-star wb-f10">{_star_svg("fs10", "#ffcad4", "#d90429")}</div>

    <div class="wb-rose-only-wrap" role="status" aria-live="polite">
      <svg class="wb-rose-3d" viewBox="0 0 150 150" aria-hidden="true">
        <defs>
          <radialGradient id="roseDeep" cx="35%" cy="25%" r="75%">
            <stop offset="0%" stop-color="#ff6b8b"/>
            <stop offset="48%" stop-color="#e11d48"/>
            <stop offset="100%" stop-color="#6b0f1a"/>
          </radialGradient>
          <radialGradient id="roseVelvet" cx="42%" cy="28%" r="70%">
            <stop offset="0%" stop-color="#ff8fa3"/>
            <stop offset="58%" stop-color="#c9184a"/>
            <stop offset="100%" stop-color="#4a0414"/>
          </radialGradient>
          <linearGradient id="roseStemGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#2d6a4f"/>
            <stop offset="50%" stop-color="#52b788"/>
            <stop offset="100%" stop-color="#1b4332"/>
          </linearGradient>
          <linearGradient id="roseLeafGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#74c69d"/>
            <stop offset="55%" stop-color="#40916c"/>
            <stop offset="100%" stop-color="#1b4332"/>
          </linearGradient>
        </defs>

        <!-- stem & lush 3D leaves -->
        <path d="M75 90 Q72 118 75 142" stroke="url(#roseStemGrad)" stroke-width="7" stroke-linecap="round" fill="none"/>
        <path d="M75 116 C52 102 36 108 40 124 C52 132 66 125 75 118 Z" fill="url(#roseLeafGrad)" stroke="#d8f3dc" stroke-width="1.1"/>
        <path d="M75 108 C98 94 114 100 110 116 C98 124 84 117 75 110 Z" fill="url(#roseLeafGrad)" stroke="#d8f3dc" stroke-width="1.1"/>

        <!-- back & side 3D petals -->
        <path d="M75 94 C38 94 20 66 30 38 C38 18 58 20 75 30 C92 20 112 18 120 38 C130 66 112 94 75 94 Z"
              fill="url(#roseDeep)" stroke="#ffccd5" stroke-width="1.3"/>
        <path d="M31 44 C24 66 42 90 75 94 C54 80 46 60 31 44 Z" fill="#590d22" opacity=".55"/>
        <path d="M119 44 C126 66 108 90 75 94 C96 80 104 60 119 44 Z" fill="#4a0414" opacity=".6"/>

        <!-- sculpted mid petals -->
        <path d="M75 88 C48 88 38 64 47 43 C54 28 66 32 75 39 C84 32 96 28 103 43 C112 64 102 88 75 88 Z"
              fill="url(#roseVelvet)" stroke="#ffb3c1" stroke-width="1.2"/>

        <!-- inner rosebud swirl -->
        <path d="M75 78 C58 78 53 58 60 45 C66 35 84 35 90 45 C97 58 92 78 75 78 Z"
              fill="#ff4d6d" stroke="#ffe5ec" stroke-width="1.2"/>
        <path d="M64 49 C68 42 82 42 86 49 C89 58 83 68 75 68 C67 68 61 58 64 49 Z"
              fill="#9d0208"/>
        <path d="M67 48 C70 44 79 45 81 51 C82 57 77 62 73 60"
              stroke="#ffb3c1" stroke-width="2" stroke-linecap="round" fill="none"/>

        <!-- soft dew / 3D light highlights -->
        <ellipse cx="48" cy="40" rx="6.5" ry="12" transform="rotate(-24 48 40)" fill="#ffffff" opacity=".36"/>
        <circle cx="96" cy="46" r="3" fill="#ffffff" opacity=".45"/>
      </svg>
    </div>
    """


def ring_svg(progress: float) -> str:
    dash = RING_C * progress
    level = 172 - 144 * progress
    wave = (
        "M0 10 Q25 0 50 10 T100 10 T150 10 T200 10 T250 10 T300 10 T350 10 "
        "T400 10 V220 H0 Z"
    )
    return f"""
    <svg viewBox="0 0 200 200" role="img" aria-label="{int(progress*100)} percent of daily goal">
      <defs>
        <linearGradient id="wbArc" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#6c5ce7"/><stop offset="1" stop-color="#5bb8e6"/>
        </linearGradient>
        <linearGradient id="wbWater" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#9d92f7" stop-opacity=".85"/>
          <stop offset="1" stop-color="#6ec1ea" stop-opacity=".75"/>
        </linearGradient>
        <clipPath id="wbClip"><circle cx="100" cy="100" r="72"/></clipPath>
      </defs>
      <circle cx="100" cy="100" r="72" fill="rgba(255,255,255,.5)"/>
      <g clip-path="url(#wbClip)">
        <g class="wb-lvl" style="transform:translateY({level:.1f}px)">
          <path class="wb-w2" d="{wave}" fill="#b8aff9" fill-opacity=".55" transform="translate(-50 -4)"/>
          <path class="wb-w1" d="{wave}" fill="url(#wbWater)"/>
        </g>
      </g>
      <circle class="wb-track" cx="100" cy="100" r="{RING_R}"/>
      <circle class="wb-arc" cx="100" cy="100" r="{RING_R}" transform="rotate(-90 100 100)"
              stroke-dasharray="{dash:.1f} {RING_C:.1f}"/>
    </svg>"""


def record_row(entry: dict) -> str:
    tag_label = entry.get("tag") or "Water"
    return (
        f'<div class="wb-rec"><div class="wb-rec-ic">💧</div>'
        f'<div><div class="wb-rec-t">{entry["time"]}</div><div class="wb-rec-s">{tag_label}</div></div>'
        f'<div class="wb-rec-ml">{entry["ml"]:,} ml<small>{fmt_liters(entry["ml"])}</small></div></div>'
    )


# ───────────────────────── Derived values ─────────────────────────
now_ist = datetime.now(TZ)
goal = max(1, int(st.session_state.daily_goal))
bottle_ml = max(50, int(st.session_state.bottle_ml))
entries = st.session_state.entries
total = sum(e["ml"] for e in entries)
remaining = max(0, goal - total)
percent = total / goal * 100
progress = min(1.0, total / goal)
avatar = AGE_AVATAR[st.session_state.age_group]
active_milestone = st.session_state.active_flower_milestone
glasses_250 = total / 250
glasses_label = f"{glasses_250:.1f}".rstrip("0").rstrip(".")
pace_label = pace_status(now_ist, percent)

if active_milestone is not None and st.session_state.sound_trigger_id > 0 and st.session_state.sound_enabled:
    play_water_then_congrats(st.session_state.sound_trigger_id)

if active_milestone is not None:
    html(single_rose_and_falling_stars_html())

# ───────────────────────── Header ─────────────────────────
hour = now_ist.hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
html(
    f"""
    <div class="wb-glass wb-hero">
      <div class="wb-avatar">{avatar}</div>
      <div>
        <div class="wb-hello">{greeting} 👋</div>
        <div class="wb-brand">WaterBuddy</div>
        <div class="wb-tag">A little water. A brighter day.</div>
      </div>
      <div class="wb-pills">
        <div class="wb-pill"><b>{goal:,} ml · {fmt_liters(goal)}</b><small>Daily goal</small></div>
        <div class="wb-pill"><b>{len(entries)}</b><small>Drinks logged</small></div>
        <div class="wb-pill"><b>{pace_label}</b><small>Daytime pace</small></div>
      </div>
    </div>
    """
)

tab_home, tab_records, tab_settings = st.tabs(["💧 Home", "🕘 Records", "⚙️ Settings"])

# ───────────────────────── Home ─────────────────────────
with tab_home:
    left, right = st.columns(2, gap="large")

    with left:
        with st.container(border=True):
            html('<div class="wb-h">Today’s progress</div>')
            ms_badges_html = "".join(
                f'<div class="wb-ms-badge{" is-done" if percent >= m else ""}">'
                f'{"🌹 " if percent >= m else ""}{m}%</div>'
                for m in MILESTONES
            )
            html(
                f"""
                <div class="wb-ring">{ring_svg(progress)}
                  <div class="wb-ring-text">
                    <div class="wb-big">{total:,}<small> ml</small></div>
                    <div class="wb-liters">{fmt_liters(total)}</div>
                    <div class="wb-of">of {goal:,} ml ({fmt_liters(goal)}) · {int(round(percent))}%</div>
                  </div>
                </div>
                <div class="wb-left"><b>{remaining:,} ml ({fmt_liters(remaining)})</b><span>left to reach your daily goal</span></div>
                <div class="wb-meta-row">
                  <span class="wb-chip">🥤 {glasses_label} glasses today</span>
                  <span class="wb-chip">🫙 Bottle: {bottle_ml:,} ml ({fmt_liters(bottle_ml)})</span>
                </div>
                <div class="wb-milestones-strip">{ms_badges_html}</div>
                <div class="wb-msg">{feedback(percent)}</div>
                """
            )
            if active_milestone is not None:
                st.button(
                    "🌹 Hide rose",
                    key="hide_flower_btn",
                    use_container_width=True,
                    on_click=dismiss_flower,
                )

    with right:
        with st.container(border=True):
            html('<div class="wb-h">Log some water</div>')
            html('<div class="wb-sub">Pick a moment tag, choose a quick pour, or log your bottle.</div>')
            st.segmented_control(
                "Drink moment",
                options=list(MOMENT_TAGS),
                key="selected_tag",
            )
            with st.container(key="quick"):
                for col, amount in zip(st.columns(len(QUICK_POURS)), QUICK_POURS):
                    col.button(
                        f"+{amount} ml ({fmt_liters(amount)})",
                        key=f"quick_{amount}",
                        use_container_width=True,
                        on_click=add_water,
                        args=(amount,),
                    )
            b_col1, b_col2 = st.columns(2)
            b_col1.button(
                f"🫙 +Bottle ({bottle_ml:,} ml · {fmt_liters(bottle_ml)})",
                key="add_bottle_btn",
                use_container_width=True,
                on_click=add_water,
                args=(bottle_ml,),
            )
            b_col2.button(
                "↩︎ Undo last",
                key="undo_home",
                disabled=not entries,
                use_container_width=True,
                on_click=undo_last,
            )
            entry_col, button_col = st.columns([2, 1], vertical_alignment="bottom")
            entry_col.number_input(
                "Or type an amount (ml)", min_value=0, max_value=3000, step=50, key="typed_amount"
            )
            button_col.button(
                "Add amount", type="primary", use_container_width=True, on_click=add_typed_water
            )

        with st.container(border=True):
            html('<div class="wb-h">Latest drinks</div>')
            if entries:
                html(
                    "<div style='display:grid;gap:8px;margin-top:8px'>"
                    + "".join(record_row(e) for e in reversed(entries[-3:]))
                    + "</div>"
                )
            else:
                html('<div class="wb-empty">No drinks yet. Tap a quick pour to start your day 💙</div>')

# ───────────────────────── Records ─────────────────────────
with tab_records:
    with st.container(border=True):
        html('<div class="wb-h">Today’s records</div>')
        largest = max((e["ml"] for e in entries), default=0)
        average = round(total / len(entries)) if entries else 0
        html(
            f"""
            <div class="wb-stats">
              <div class="wb-stat"><b>{total:,} ml</b><span>{fmt_liters(total)}</span><small>Total</small></div>
              <div class="wb-stat"><b>{average:,} ml</b><span>{fmt_liters(average)}</span><small>Average</small></div>
              <div class="wb-stat"><b>{largest:,} ml</b><span>{fmt_liters(largest)}</span><small>Largest</small></div>
            </div>
            """
        )
        if entries:
            with st.container(key="records"):
                for idx in range(len(entries) - 1, -1, -1):
                    row, btn = st.columns([5, 1], vertical_alignment="center")
                    with row:
                        html(record_row(entries[idx]))
                    btn.button(
                        "✕",
                        key=f"del_{idx}_{entries[idx]['time']}",
                        on_click=remove_entry,
                        args=(idx,),
                        help="Remove this entry",
                    )
        else:
            html('<div class="wb-empty">Nothing logged yet today.</div>')

    if st.session_state.show_reset_confirm:
        with st.container(border=True):
            html('<div class="wb-h">Start a new day?</div>')
            html('<div class="wb-sub">This clears today’s drinks and sets your total back to 0 ml (0 L).</div>')
            c1, c2 = st.columns(2)
            c1.button("Yes, reset", type="primary", use_container_width=True, on_click=reset_new_day)
            c2.button("Cancel", use_container_width=True, on_click=cancel_new_day)
    else:
        st.button("🌅 New day", on_click=ask_new_day)

# ───────────────────────── Settings ─────────────────────────
with tab_settings:
    with st.container(border=True):
        html('<div class="wb-h">Set your daily target</div>')
        html(
            f'<div class="wb-sub">Current goal: <b>{goal:,} ml ({fmt_liters(goal)})</b> · '
            f'Bottle preset: <b>{bottle_ml:,} ml ({fmt_liters(bottle_ml)})</b>.</div>'
        )
        s1, s2 = st.columns(2, gap="medium")
        s1.selectbox("Age group", list(AGE_GOALS), key="age_group", on_change=set_goal_from_age)
        s2.number_input(
            "Daily goal (ml)",
            min_value=250,
            max_value=6000,
            step=50,
            key="daily_goal",
            on_change=_sync_milestones,
        )
        s3, s4 = st.columns(2, gap="medium", vertical_alignment="center")
        s3.number_input(
            "Favorite bottle size (ml)",
            min_value=100,
            max_value=2500,
            step=50,
            key="bottle_ml",
        )
        s4.toggle("Milestone sound & voice", key="sound_enabled")

st.caption("Your progress stays in this browser session and is not sent to an account.")
