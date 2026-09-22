import streamlit as st
import random
import time
import json
import requests
import base64
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="BT Wheel Of Names",
    page_icon="🏆",
    layout="centered"
)

TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]

WINNER_FILE = "winner_history.json"
PARTICIPANT_FILE = "participants.json"

# --------------------------------------------------
# GITHUB HELPERS
# --------------------------------------------------

def github_get(filename):

    url = f"https://api.github.com/repos/{REPO}/contents/{filename}"

    headers = {
        "Authorization": f"token {TOKEN}"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return []

    data = r.json()

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    return json.loads(content)

def github_save(filename, content_data):

    url = f"https://api.github.com/repos/{REPO}/contents/{filename}"

    headers = {
        "Authorization": f"token {TOKEN}"
    }

    get_file = requests.get(
        url,
        headers=headers
    )

    if get_file.status_code != 200:
        raise Exception(
            f"Unable to access {filename}"
        )

    sha = get_file.json()["sha"]

    encoded = base64.b64encode(
        json.dumps(
            content_data,
            indent=4
        ).encode("utf-8")
    ).decode()

    payload = {
        "message": f"Update {filename}",
        "content": encoded,
        "sha": sha
    }

    save = requests.put(
        url,
        headers=headers,
        json=payload
    )

    if save.status_code not in [200, 201\]:
        raise Exception(save.text)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

history_data = github_get(
    WINNER_FILE
)

participant_data = github_get(
    PARTICIPANT_FILE
)

if not participant_data:
    participant_data = [
        "Harsha",
        "Harish",
        "Sudhakar"
    ]

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "winner_history" not in st.session_state:
    st.session_state.winner_history = history_data

if "participants" not in st.session_state:
    st.session_state.participants = participant_data

if "winner" not in st.session_state:
    st.session_state.winner = None

# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown("""
<style>

.main-title{
text-align:center;
font-size:48px;
font-weight:bold;
color:#ff4b4b;
}

.sub-title{
text-align:center;
color:gray;
margin-bottom:20px;
}

.spin-card{
background:linear-gradient(135deg,#111827,#1F2937);
color:white;
text-align:center;
border-radius:20px;
padding:50px;
margin-top:15px;
margin-bottom:15px;
font-size:42px;
font-weight:bold;
border:3px solid #ff4b4b;
}

.winner-card{
background:linear-gradient(135deg,#FFD700,#FFA500);
color:black;
text-align:center;
padding:35px;
border-radius:25px;
font-size:32px;
font-weight:bold;
box-shadow:0px 5px 20px rgba(0,0,0,0.3);
}

.history-box{
background:#f4f4f4;
padding:15px;
border-radius:15px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎡 Wheel Of Names</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Spin & Select a Champion</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# PARTICIPANTS
# --------------------------------------------------

with st.expander(
    "👥 Manage Participants",
    expanded=True
):

    participant_text = st.text_area(
        "One name per line",
        value="\n".join(
            st.session_state.participants
        ),
        height=250
    )

    if st.button(
        "💾 Save Participants",
        use_container_width=True
    ):

        new_list = [

            x.strip()

            for x in participant_text.splitlines()

            if x.strip()
        ]

        st.session_state.participants = (
            new_list
        )

        try:
            github_save(
                PARTICIPANT_FILE,
                new_list
            )

            st.success(
                "Participants saved."
            )

        except Exception as e:
            st.error(str(e))

participants = st.session_state.participants

# --------------------------------------------------
# BUTTONS
# --------------------------------------------------

col1, col2 = st.columns(2)

spin_btn = col1.button(
    "🎯 SPIN WHEEL",
    use_container_width=True
)

reset_btn = col2.button(
    "🗑 RESET HISTORY",
    use_container_width=True
)

# --------------------------------------------------
# RESET HISTORY
# --------------------------------------------------

if reset_btn:

    st.session_state.winner_history = []
    st.session_state.winner = None

    try:

        github_save(
            WINNER_FILE,
            []
        )

        st.success(
            "History Reset Successfully"
        )

    except Exception as e:
        st.error(str(e))

# --------------------------------------------------
# SPIN
# --------------------------------------------------

spin_area = st.empty()

if spin_btn:

    recent = [

        x["name"]

        for x in st.session_state.winner_history
    ]

    eligible = [

        p

        for p in participants

        if p not in recent
    ]

    if not eligible:
        eligible = participants

    winner = random.choice(
        eligible
    )

    delay = 0.04

    for _ in range(45):

        current = random.choice(
            participants
        )

        spin_area.markdown(
            f"""
            <div class="spin-card">
            🎡<br><br>
            {current}
            </div>
            """,
            unsafe_allow_html=True
        )

        time.sleep(delay)

        delay += 0.004

    spin_area.markdown(
        f"""
        <div class="spin-card">
        🏆<br><br>
        {winner}
        </div>
        """,
        unsafe_allow_html=True
    )

    winner_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )

    record = {
        "name": winner,
        "date": winner_time
    }

    st.session_state.winner = record

    st.session_state.winner_history.insert(
        0,
        record
    )

    st.session_state.winner_history = (
        st.session_state.winner_history[:4]
    )

    try:

        github_save(
            WINNER_FILE,
            st.session_state.winner_history
        )

    except Exception as e:
        st.error(str(e))

    st.balloons()

# --------------------------------------------------
 RECOVER LAST WINNER
# --------------------------------------------------

if (
    st.session_state.winner is None
    and st.session_state.winner_history
):
    st.session_state.winner = (
        st.session_state.winner_history[0]
    )

# --------------------------------------------------
# WINNER CARD
# --------------------------------------------------

if st.session_state.winner:

    st.markdown(
        f"""
        <div class="winner-card">
        🏆 WINNER 🏆
        <br><br>
        👑 {st.session_state.winner['name']}
        <br><br>
        🎉 Congratulations 🎉
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# LAST 4 WINNERS
# --------------------------------------------------

st.markdown("---")

st.subheader(
    "🏅 Last 4 Winners"
)

if st.session_state.winner_history:

    st.markdown(
        "<div class='history-box'>",
        unsafe_allow_html=True
    )

    for i, item in enumerate(
        st.session_state.winner_history,
        start=1
    ):

        st.write(
            f"{i}. 🏆 {item['name']} | 📅 {item['date']}"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

else:

    st.info(
        "No winners yet."
    )

# --------------------------------------------------
# STATS
# --------------------------------------------------

st.markdown("---")

st.metric(
    "👥 Total Participants",
    len(participants)
)
