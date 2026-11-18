import streamlit as st
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="WaterBuddy | Daily Hydration Companion",
    page_icon="💧",
    layout="centered"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
    }
    .mascot-box {
        background-color: #e0f7fa;
        border-left: 6px solid #00acc1;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        color: #004d40;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA & CONSTANTS ---
AGE_GOALS = {
    "6–12 years (Kids)": 1600,
    "13–18 years (Teens)": 2200,
    "19–50 years (Adults)": 2500,
    "65+ years (Seniors)": 2000
}

HYDRATION_TIPS = [
    "Start your morning with one full glass of water right after waking up!",
    "Keep a reusable water bottle on your study desk as a visual reminder.",
    "Drink a glass of water 20 minutes before every meal to help digestion.",
    "Feeling tired or unfocused? Mild dehydration is often the hidden cause.",
    "Add a slice of lemon, cucumber, or mint if plain water feels boring!"
]

# --- SESSION STATE ---
if "intake" not in st.session_state:
    st.session_state.intake = 0
if "daily_tip" not in st.session_state:
    st.session_state.daily_tip = random.choice(HYDRATION_TIPS)
if "selected_age" not in st.session_state:
    st.session_state.selected_age = "13–18 years (Teens)"
if "custom_goal" not in st.session_state:
    st.session_state.custom_goal = AGE_GOALS[st.session_state.selected_age]

# --- FUNCTIONS ---
def update_age_goal():
    st.session_state.custom_goal = AGE_GOALS[st.session_state.selected_age]

def add_water(amount):
    st.session_state.intake += amount

def reset_day():
    st.session_state.intake = 0
    st.session_state.daily_tip = random.choice(HYDRATION_TIPS)

def get_mascot_feedback(percentage):
    if percentage == 0:
        return "🐢 Droplet the Turtle says:", "Ready to start your day? Take your first sip!"
    elif percentage < 50:
        return "🐬 Splash the Dolphin cheers:", "Great start! Keep sipping steadily through the day."
    elif percentage < 100:
        return "🐳 Wave the Whale says:", "Awesome! Over halfway there—keep going!"
    else:
        return "🏆 Hydration Champion!", "100% Goal Reached! Amazing job staying hydrated today!"

def render_visual_bottle(percentage):
    fill_height = min(int(percentage), 100)
    bottle_html = f"""
    <div style="display: flex; justify-content: center; margin: 15px 0;">
        <div style="width: 90px; height: 180px; border: 4px solid #0288d1; border-radius: 15px 15px 25px 25px; position: relative; overflow: hidden; background-color: #ffffff; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div style="position: absolute; bottom: 0; width: 100%; height: {fill_height}%; background: linear-gradient(180deg, #4fc3f7 0%, #0288d1 100%);"></div>
            <div style="position: absolute; width: 100%; text-align: center; top: 42%; font-weight: bold; color: #01579b; font-size: 16px;">
                {fill_height}%
            </div>
        </div>
    </div>
    """
    st.markdown(bottle_html, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("💡 Daily Hydration Tip")
    st.info(st.session_state.daily_tip)
    if st.button("New Tip 🔄"):
        st.session_state.daily_tip = random.choice(HYDRATION_TIPS)
        st.rerun()

# --- MAIN INTERFACE ---
st.title("💧 WaterBuddy")
st.subheader("Your Friendly Daily Hydration Companion")

col_age, col_goal = st.columns(2)
with col_age:
    st.selectbox("Select your age group:", options=list(AGE_GOALS.keys()), key="selected_age", on_change=update_age_goal)
with col_goal:
    goal = st.number_input("Daily Goal (ml):", min_value=500, max_value=6000, step=100, key="custom_goal")

st.divider()

col_btn1, col_btn2, col_custom = st.columns([1, 1, 2])
with col_btn1:
    st.write("")
    if st.button("➕ +250 ml", use_container_width=True, type="primary"):
        add_water(250)
with col_btn2:
    st.write("")
    if st.button("➕ +500 ml", use_container_width=True):
        add_water(500)
with col_custom:
    custom_amount = st.number_input("Custom ml:", min_value=50, max_value=2000, value=150, step=50)
    if st.button("Log Custom 💦", use_container_width=True):
        add_water(custom_amount)

st.divider()

total_intake = st.session_state.intake
remaining = max(goal - total_intake, 0)
percentage = (total_intake / goal) * 100 if goal > 0 else 0

m1, m2, m3 = st.columns(3)
m1.metric("Total Intake", f"{total_intake} ml")
m2.metric("Remaining", f"{remaining} ml")
m3.metric("Goal Achieved", f"{min(int(percentage), 100)}%")

st.progress(min(percentage / 100, 1.0))
render_visual_bottle(percentage)

mascot_title, mascot_msg = get_mascot_feedback(percentage)
st.markdown(f"""
<div class="mascot-box">
    <strong>{mascot_title}</strong><br>
    {mascot_msg}
</div>
""", unsafe_allow_html=True)

if percentage >= 100:
    st.balloons()

st.divider()
if st.button("🔄 Reset Day", use_container_width=True):
    reset_day()
    st.rerun()