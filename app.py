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
TZ = ZoneInfo("Asia/Kolkata")  # change to your users' timezone
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

# ───────────────────────── State & callbacks ─────────────────────────
DEFAULTS = {
    "age_group": "Adults (14 to 64)",
    "daily_goal": AGE_GOALS["Adults (14 to 64)"],
    "entries": [],  # list of {"ml": int, "time": "03:00 PM"}
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
            st.session_state.sound_trigger_id += 1
    elif (
        st.session_state.active_flower_milestone is not None
        and pct < st.session_state.active_flower_milestone
    ):
        st.session_state.active_flower_milestone = None


def add_water(amount):
    amount = int(amount or 0)
    if amount > 0:
        st.session_state.entries.append(
            {"ml": amount, "time": datetime.now(TZ).strftime("%I:%M %p")}
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root{
  --ink:#25235a; --ink-soft:#5f5f93; --accent:#6c5ce7; --accent-2:#8d7ff5;
  --sky:#a9d2ea; --lav:#d6d0f8;
  --glass:rgba(255,255,255,.36); --glass-strong:rgba(255,255,255,.58);
  --edge:rgba(255,255,255,.72);
  --shadow:0 18px 44px rgba(84,72,170,.16);
  color-scheme: light;
}

/* ── base + animated liquid backdrop ── */
html, body, .stApp, [data-testid="stAppViewContainer"]{
  color-scheme: light !important; color: var(--ink);
  background: linear-gradient(155deg,#bfe0f0 0%,#d9d3f8 52%,#c2d8f2 100%) fixed !important;
}
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4{
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
.stApp::before, .stApp::after{
  content:""; position:fixed; z-index:0; pointer-events:none; border-radius:50%;
  filter:blur(60px); opacity:.75;
}
.stApp::before{ width:46vmax; height:46vmax; left:-14vmax; top:-12vmax;
  background:radial-gradient(circle,#9a8cff 0%,transparent 68%); animation:drift 22s ease-in-out infinite alternate; }
.stApp::after{ width:42vmax; height:42vmax; right:-12vmax; bottom:-14vmax;
  background:radial-gradient(circle,#6fc3e8 0%,transparent 68%); animation:drift 26s ease-in-out infinite alternate-reverse; }
@keyframes drift{ to{ transform:translate(6vmax,4vmax) scale(1.08); } }

[data-testid="stHeader"]{ background:transparent !important; }
#MainMenu, footer, [data-testid="stDecoration"]{ display:none !important; }
[data-testid="stMainBlockContainer"], .block-container{
  position:relative; z-index:1; max-width:1120px; margin:0 auto;
  padding:clamp(.8rem,2.5vw,2rem) clamp(.8rem,3vw,2rem) 4rem;
}

/* ── liquid glass surfaces ── */
.wb-glass, [data-testid="stVerticalBlockBorderWrapper"]{
  position:relative; overflow:hidden;
  background:linear-gradient(135deg,rgba(255,255,255,.52),rgba(255,255,255,.22)) !important;
  -webkit-backdrop-filter:blur(24px) saturate(170%); backdrop-filter:blur(24px) saturate(170%);
  border:1px solid var(--edge) !important; border-radius:28px !important;
  box-shadow:inset 0 1.5px 0 rgba(255,255,255,.95), inset 0 -1px 0 rgba(255,255,255,.25), var(--shadow);
}
.wb-glass::before, [data-testid="stVerticalBlockBorderWrapper"]::before{
  content:""; position:absolute; inset:0; pointer-events:none; border-radius:inherit;
  background:radial-gradient(120% 70% at 12% -10%,rgba(255,255,255,.55),transparent 55%);
}
[data-testid="stVerticalBlockBorderWrapper"] > div{ position:relative; }
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:20px !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.9);
}

/* ── header ── */
.wb-hero{ display:flex; align-items:center; gap:clamp(12px,2.4vw,20px); padding:clamp(16px,3vw,26px); margin-bottom:1rem; }
.wb-avatar{ flex:0 0 auto; width:clamp(54px,9vw,72px); aspect-ratio:1; display:grid; place-items:center;
  font-size:clamp(28px,5vw,38px); border-radius:50%;
  background:linear-gradient(145deg,#fff,#e4defc); box-shadow:inset 0 -3px 8px rgba(108,92,231,.18),0 8px 20px rgba(108,92,231,.25); }
.wb-hello{ color:var(--ink-soft); font-size:.9rem; font-weight:600; }
.wb-brand{ font-size:clamp(1.5rem,4vw,2.1rem); font-weight:800; letter-spacing:-.03em; line-height:1.1; }
.wb-tag{ color:var(--ink-soft); font-size:.92rem; margin-top:2px; }
.wb-pills{ margin-left:auto; display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
.wb-pill{ padding:9px 14px; border-radius:18px; background:var(--glass-strong); border:1px solid var(--edge);
  text-align:center; min-width:110px; box-shadow:inset 0 1px 0 #fff; }
.wb-pill b{ display:block; font-size:1.02rem; font-weight:800; }
.wb-pill small{ color:var(--ink-soft); font-size:.7rem; font-weight:600; }

/* ── section titles ── */
.wb-h{ font-size:1.12rem; font-weight:800; letter-spacing:-.01em; margin:.1rem 0 .15rem; }
.wb-sub{ color:var(--ink-soft); font-size:.88rem; margin-bottom:.7rem; }

/* ── progress ring with liquid wave ── */
.wb-ring{ position:relative; width:min(100%,300px); margin:.4rem auto .6rem; aspect-ratio:1; }
.wb-ring svg{ width:100%; height:100%; display:block; overflow:visible; }
.wb-track{ fill:none; stroke:rgba(255,255,255,.7); stroke-width:12; }
.wb-arc{ fill:none; stroke:url(#wbArc); stroke-width:12; stroke-linecap:round;
  transition:stroke-dasharray .9s cubic-bezier(.22,1,.36,1); filter:drop-shadow(0 4px 8px rgba(108,92,231,.35)); }
.wb-lvl{ transition:transform 1s cubic-bezier(.22,1,.36,1); }
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
.wb-msg{ margin-top:10px; padding:13px 16px; border-radius:18px; font-weight:700; line-height:1.4;
  background:linear-gradient(135deg,rgba(108,92,231,.16),rgba(111,195,232,.2)); border:1px solid var(--edge); }

/* ── big screen-stage blossom + 3D stars (doesn't cover whole screen) ── */
.wb-stage{
  position:relative;
  margin-top:14px;
  padding:22px 18px 20px;
  border-radius:26px;
  background:
    radial-gradient(circle at 50% 28%, rgba(255,255,255,.92), rgba(248,234,255,.68) 60%, rgba(214,238,255,.55) 100%);
  border:1.5px solid rgba(255,255,255,.95);
  box-shadow:0 20px 44px rgba(108,92,231,.24), inset 0 1.5px 0 #fff;
  overflow:hidden;
  perspective:900px;
  animation:stagePop .72s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes stagePop{
  0%{ opacity:0; transform:translateY(24px) scale(.86) rotateX(14deg); }
  100%{ opacity:1; transform:translateY(0) scale(1) rotateX(0deg); }
}

.wb-stage-center{
  position:relative;
  z-index:2;
  display:flex;
  flex-direction:column;
  align-items:center;
  text-align:center;
}

.wb-congrats{
  font-size:clamp(1.35rem,3.4vw,1.95rem);
  font-weight:800;
  letter-spacing:.06em;
  text-transform:uppercase;
  background:linear-gradient(135deg,#6c5ce7 0%,#e84393 52%,#ff9f1c 100%);
  -webkit-background-clip:text;
  background-clip:text;
  color:transparent;
  margin-top:4px;
  animation:congratsBounce .85s cubic-bezier(.34,1.56,.64,1) .15s both;
}
@keyframes congratsBounce{
  0%{ opacity:0; transform:translateY(14px) scale(.75); }
  100%{ opacity:1; transform:translateY(0) scale(1); }
}

.wb-milestone-pill{
  font-size:.76rem;
  font-weight:800;
  color:#7b2cbf;
  background:rgba(255,255,255,.85);
  border:1px solid rgba(232,121,168,.45);
  padding:4px 12px;
  border-radius:999px;
  margin-top:6px;
}

.wb-stage-sub{
  font-size:.88rem;
  font-weight:600;
  color:var(--ink-soft);
  margin-top:5px;
  max-width:34ch;
}

.wb-bloom-flower{
  width:clamp(128px,26vw,176px);
  height:clamp(128px,26vw,176px);
  overflow:visible;
  transform-origin:50% 62%;
  filter:drop-shadow(0 12px 22px rgba(232,121,168,.35));
  animation:popBlossom .9s cubic-bezier(.34,1.56,.64,1) .05s both, gentleFloat 3.4s ease-in-out 1s infinite alternate;
}
@keyframes popBlossom{
  0%{ opacity:0; transform:scale(.15) rotate(-40deg); }
  62%{ opacity:1; transform:scale(1.14) rotate(7deg); }
  100%{ opacity:1; transform:scale(1) rotate(0deg); }
}
@keyframes gentleFloat{
  0%{ transform:translateY(0px) rotate(-3deg) scale(1); }
  100%{ transform:translateY(-6px) rotate(3deg) scale(1.04); }
}

/* ── cute 3D-style tumbling stars around the flower ── */
.wb-star-3d{
  position:absolute;
  z-index:1;
  pointer-events:none;
  transform-style:preserve-3d;
  filter:drop-shadow(0 6px 10px rgba(108,92,231,.28));
}
.wb-star-3d svg{ width:100%; height:100%; display:block; }

.wb-s1{ width:34px; height:34px; top:12%; left:8%;
  animation:star3dA 3.8s ease-in-out infinite; }
.wb-s2{ width:28px; height:28px; top:16%; right:10%;
  animation:star3dB 4.2s ease-in-out .3s infinite; }
.wb-s3{ width:38px; height:38px; bottom:18%; left:6%;
  animation:star3dB 3.5s ease-in-out .6s infinite; }
.wb-s4{ width:30px; height:30px; bottom:16%; right:8%;
  animation:star3dA 4.0s ease-in-out .2s infinite; }
.wb-s5{ width:24px; height:24px; top:48%; left:4%;
  animation:star3dA 3.2s ease-in-out .8s infinite; }
.wb-s6{ width:26px; height:26px; top:46%; right:4%;
  animation:star3dB 3.6s ease-in-out .4s infinite; }

@keyframes star3dA{
  0%,100%{ transform:translateY(0px) rotateY(0deg) rotateZ(0deg) scale(.92); }
  50%{ transform:translateY(-10px) rotateY(180deg) rotateZ(18deg) scale(1.14); }
}
@keyframes star3dB{
  0%,100%{ transform:translateY(0px) rotateX(0deg) rotateZ(0deg) scale(1); }
  50%{ transform:translateY(-12px) rotateX(180deg) rotateZ(-20deg) scale(1.16); }
}

/* ── records ── */
.wb-rec{ display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:18px;
  background:var(--glass-strong); border:1px solid var(--edge); box-shadow:inset 0 1px 0 #fff; }
.wb-rec-ic{ width:38px; height:38px; border-radius:13px; display:grid; place-items:center; font-size:1.1rem;
  background:linear-gradient(145deg,#e7e2fd,#cfe7f6); flex:0 0 auto; }
.wb-rec-t{ font-weight:700; font-size:.95rem; } .wb-rec-s{ color:var(--ink-soft); font-size:.78rem; }
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

/* ── inputs ── */
.stApp label, .stApp [data-testid="stWidgetLabel"] p{ color:var(--ink) !important; font-weight:700 !important; }
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"]{
  background:rgba(255,255,255,.7) !important; border-radius:16px !important; border-color:var(--edge) !important;
}
[data-baseweb="select"] *, [data-baseweb="input"] input{ color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] ul{ background:rgba(255,255,255,.92) !important; border-radius:16px !important; }
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
  .stApp::before,.stApp::after,.wb-w1,.wb-w2,.wb-stage,.wb-congrats,.wb-bloom-flower,.wb-star-3d{ animation:none !important; }
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
        return "Great job! You reached your goal today! 🎉"
    if percent >= 75:
        return "Almost there! You are past 75%. 🌊"
    if percent >= 50:
        return "Great! You reached 50%! 😊"
    return "You’re doing well. Every glass gets you closer! 💙"


def play_pop_chime(trigger_id: int) -> None:
    """Play a balloon-pop burst + bright blossom chime via Web Audio API."""
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

            // 1) Crisp balloon-pop thump + snap
            const popOsc = ctx.createOscillator();
            const popGain = ctx.createGain();
            popOsc.type = "triangle";
            popOsc.frequency.setValueAtTime(340, now);
            popOsc.frequency.exponentialRampToValueAtTime(58, now + 0.11);

            popGain.gain.setValueAtTime(0.001, now);
            popGain.gain.linearRampToValueAtTime(0.45, now + 0.008);
            popGain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

            popOsc.connect(popGain);
            popGain.connect(ctx.destination);
            popOsc.start(now);
            popOsc.stop(now + 0.13);

            // Short air burst for realistic pop transient
            const bufferSize = Math.floor(ctx.sampleRate * 0.05);
            const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = noiseBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {{
              data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.35));
            }}
            const noise = ctx.createBufferSource();
            noise.buffer = noiseBuffer;
            const filter = ctx.createBiquadFilter();
            filter.type = "bandpass";
            filter.frequency.setValueAtTime(1400, now);
            filter.Q.setValueAtTime(1.8, now);
            const noiseGain = ctx.createGain();
            noiseGain.gain.setValueAtTime(0.32, now);
            noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
            noise.connect(filter);
            filter.connect(noiseGain);
            noiseGain.connect(ctx.destination);
            noise.start(now);

            // 2) Cheerful flower-blossom arpeggio right after the pop
            const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
            notes.forEach((freq, idx) => {{
              const start = now + 0.07 + idx * 0.075;
              const osc = ctx.createOscillator();
              const gain = ctx.createGain();
              osc.type = "sine";
              osc.frequency.setValueAtTime(freq, start);
              gain.gain.setValueAtTime(0.001, start);
              gain.gain.linearRampToValueAtTime(0.14, start + 0.015);
              gain.gain.exponentialRampToValueAtTime(0.0008, start + 0.32);
              osc.connect(gain);
              gain.connect(ctx.destination);
              osc.start(start);
              osc.stop(start + 0.34);
            }});
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def _star_3d_svg(fill_top: str, fill_bottom: str) -> str:
    return f"""
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id="st_{fill_top.strip('#')}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{fill_top}"/>
          <stop offset="100%" stop-color="{fill_bottom}"/>
        </linearGradient>
      </defs>
      <polygon points="24,3 29.8,16.4 44.3,17.8 33.3,27.3 36.6,41.6 24,34 11.4,41.6 14.7,27.3 3.7,17.8 18.2,16.4"
               fill="url(#st_{fill_top.strip('#')})" stroke="#ffffff" stroke-width="1.6" stroke-linejoin="round"/>
      <polygon points="24,3 29.8,16.4 24,20.5" fill="#ffffff" opacity=".45"/>
    </svg>
    """


def blossom_stage_html(milestone: int) -> str:
    messages = {
        25: "You hit 25% of your daily goal—your flower popped into bloom!",
        50: "Halfway to your target at 50%—keep that fresh energy flowing!",
        75: "75% complete—your hydration blossom is shining bright!",
        100: "100% goal achieved—full flower power for staying hydrated!",
    }
    sub = messages.get(milestone, f"You crossed {milestone}% of your daily hydration target!")
    return f"""
    <div class="wb-stage" role="status" aria-live="polite">
      <div class="wb-star-3d wb-s1">{_star_3d_svg("#ffe066", "#ff9f1c")}</div>
      <div class="wb-star-3d wb-s2">{_star_3d_svg("#ff9ebb", "#e84393")}</div>
      <div class="wb-star-3d wb-s3">{_star_3d_svg("#9bf6ff", "#4cc9f0")}</div>
      <div class="wb-star-3d wb-s4">{_star_3d_svg("#bdb2ff", "#6c5ce7")}</div>
      <div class="wb-star-3d wb-s5">{_star_3d_svg("#ffd6a5", "#f77f00")}</div>
      <div class="wb-star-3d wb-s6">{_star_3d_svg("#caffbf", "#2ec4b6")}</div>

      <div class="wb-stage-center">
        <svg class="wb-bloom-flower" viewBox="0 0 120 120" aria-hidden="true">
          <defs>
            <radialGradient id="wbPetalMain" cx="50%" cy="30%" r="70%">
              <stop offset="0%" stop-color="#ffe0ec"/>
              <stop offset="55%" stop-color="#ff8fab"/>
              <stop offset="100%" stop-color="#e84393"/>
            </radialGradient>
            <radialGradient id="wbFlowerCenter" cx="40%" cy="35%" r="65%">
              <stop offset="0%" stop-color="#fff6b3"/>
              <stop offset="100%" stop-color="#ffb703"/>
            </radialGradient>
          </defs>
          <!-- stem & leaves -->
          <path d="M60 72 Q58 94 60 112" stroke="#38b000" stroke-width="6" stroke-linecap="round" fill="none"/>
          <path d="M60 95 Q38 86 35 100 Q48 106 60 98 Z" fill="#55a630"/>
          <path d="M60 88 Q82 79 85 93 Q72 99 60 91 Z" fill="#38b000"/>

          <!-- 8 lush petals -->
          <g fill="url(#wbPetalMain)" stroke="#ffffff" stroke-width="1.2">
            <ellipse cx="60" cy="27" rx="12" ry="20"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(45 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(90 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(135 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(180 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(225 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(270 60 54)"/>
            <ellipse cx="60" cy="27" rx="12" ry="20" transform="rotate(315 60 54)"/>
          </g>

          <!-- happy blossom face -->
          <circle cx="60" cy="54" r="17" fill="url(#wbFlowerCenter)" stroke="#fff" stroke-width="2"/>
          <circle cx="54.5" cy="52" r="2.1" fill="#3d2c1e"/>
          <circle cx="65.5" cy="52" r="2.1" fill="#3d2c1e"/>
          <circle cx="51" cy="55.5" r="2.5" fill="#ff758f" opacity=".7"/>
          <circle cx="69" cy="55.5" r="2.5" fill="#ff758f" opacity=".7"/>
          <path d="M56 57.5 Q60 62 64 57.5" stroke="#3d2c1e" stroke-width="2.2" stroke-linecap="round" fill="none"/>
        </svg>

        <div class="wb-congrats">CONGRATULATIONS!</div>
        <div class="wb-milestone-pill">🌸 {milestone}% Goal Milestone</div>
        <div class="wb-stage-sub">{sub}</div>
      </div>
    </div>
    """


def ring_svg(progress: float) -> str:
    dash = RING_C * progress
    level = 172 - 144 * progress  # inner circle spans y=28 → y=172
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
    return (
        f'<div class="wb-rec"><div class="wb-rec-ic">💧</div>'
        f'<div><div class="wb-rec-t">{entry["time"]}</div><div class="wb-rec-s">Water</div></div>'
        f'<div class="wb-rec-ml">{entry["ml"]:,} ml<small>{fmt_liters(entry["ml"])}</small></div></div>'
    )


# ───────────────────────── Derived values ─────────────────────────
goal = max(1, int(st.session_state.daily_goal))
entries = st.session_state.entries
total = sum(e["ml"] for e in entries)
remaining = max(0, goal - total)
percent = total / goal * 100
progress = min(1.0, total / goal)
avatar = AGE_AVATAR[st.session_state.age_group]
active_milestone = st.session_state.active_flower_milestone

# Trigger pop + chime sound when a new milestone unlocks
if active_milestone is not None and st.session_state.sound_trigger_id > 0:
    play_pop_chime(st.session_state.sound_trigger_id)

# ───────────────────────── Header ─────────────────────────
hour = datetime.now(TZ).hour
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
            stage_html = blossom_stage_html(active_milestone) if active_milestone is not None else ""
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
                <div class="wb-msg">{feedback(percent)}</div>
                {stage_html}
                """
            )
            if active_milestone is not None:
                st.button(
                    "✨ Hide celebration",
                    key="hide_flower_btn",
                    use_container_width=True,
                    on_click=dismiss_flower,
                )

    with right:
        with st.container(border=True):
            html('<div class="wb-h">Log some water</div>')
            html('<div class="wb-sub">Choose a quick pour or enter your own amount.</div>')
            with st.container(key="quick"):
                for col, amount in zip(st.columns(len(QUICK_POURS)), QUICK_POURS):
                    col.button(
                        f"+{amount} ml ({fmt_liters(amount)})",
                        key=f"quick_{amount}",
                        use_container_width=True,
                        on_click=add_water,
                        args=(amount,),
                    )
            entry_col, button_col = st.columns([2, 1], vertical_alignment="bottom")
            entry_col.number_input(
                "Or type an amount (ml)", min_value=0, max_value=3000, step=50, key="typed_amount"
            )
            button_col.button(
                "Add amount", type="primary", use_container_width=True, on_click=add_typed_water
            )
            st.button(
                "↩︎ Undo last",
                key="undo_home",
                disabled=not entries,
                use_container_width=True,
                on_click=undo_last,
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
            f'<div class="wb-sub">Current goal: <b>{goal:,} ml ({fmt_liters(goal)})</b>. '
            'Choose an age group or adjust anytime.</div>'
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

st.caption("Your progress stays in this browser session and is not sent to an account.")
