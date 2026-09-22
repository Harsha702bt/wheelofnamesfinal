import streamlit as st
import random
import time
import json
import requests
import base64
from datetime import datetime
from zoneinfo import ZoneInfo

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="BT Wheel Of Names",
    page_icon="🏆",
    layout="centered"
)

# --------------------------------------------------
# GITHUB CONFIG
# --------------------------------------------------

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]

WINNER_FILE = "winner_history.json"
PARTICIPANT_FILE = "participants.json"

# --------------------------------------------------
# GITHUB FUNCTIONS
# --------------------------------------------------

def load_github_json(filename):

    try:

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

        r = requests.get(url, headers=headers)

        if r.status_code == 200:

            content = base64.b64decode(
                r.json()["content"]
            ).decode("utf-8")

            return json.loads(content)

    except:
        pass

    return []

def save_github_json(filename, data):

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    r = requests.get(url, headers=headers)

    sha = r.json()["sha"]

    new_content = base64.b64encode(
        json.dumps(data, indent=4).encode()
    ).decode()

    payload = {
        "message": f"Update {filename}",
        "content": new_content,
        "sha": sha
    }

    requests.put(
        url,
        headers=headers,
        json=payload
    )

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

winner_history = load_github_json(
    WINNER_FILE
)

participants = load_github_json(
    PARTICIPANT_FILE
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "winner" not in st.session_state:
    st.session_state.winner = None

if "winner_history" not in st.session_state:
    st.session_state.winner_history = winner_history

if "participants" not in st.session_state:
    st.session_state.participants = participants

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎡 BT Wheel Of Names")

# --------------------------------------------------
# MANAGE PARTICIPANTS
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
        "💾 Save Participants"
    ):

        updated = [

            p.strip()
            for p in participant_text.splitlines()
            if p.strip()
        ]

        st.session_state.participants = updated

        save_github_json(
            PARTICIPANT_FILE,
            updated
        )

        st.success(
            "Participants Saved"
        )

participants = st.session_state.participants

# --------------------------------------------------
# BUTTONS
# --------------------------------------------------

col1, col2 = st.columns(2)

spin = col1.button(
    "🎯 SPIN WHEEL",
    use_container_width=True
)

reset = col2.button(
    "🗑 RESET HISTORY",
    use_container_width=True
)

# --------------------------------------------------
# RESET
# --------------------------------------------------

if reset:

    st.session_state.winner_history = []
    st.session_state.winner = None

    save_github_json(
        WINNER_FILE,
        []
    )

    st.success(
        "History Reset Successfully"
    )

# --------------------------------------------------
# SPIN
# --------------------------------------------------

if spin:

    recent_names = [

        item["name"]

        for item in st.session_state.winner_history
    ]

    eligible = [

        p

        for p in participants

        if p not in recent_names
    ]

    if not eligible:
        eligible = participants

    selected_winner = random.choice(
        eligible
    )

    spin_placeholder = st.empty()

    speed = 0.04

    for _ in range(40):

        spin_placeholder.info(
            random.choice(participants)
        )

        time.sleep(speed)

        speed += 0.003

    spin_placeholder.success(
        f"🏆 {selected_winner}"
    )

    winner_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )

    winner_record = {
        "name": selected_winner,
        "date": winner_time
    }

    st.session_state.winner = (
        winner_record
    )

    st.session_state.winner_history.insert(
        0,
        winner_record
    )

    st.session_state.winner_history = (
        st.session_state.winner_history[:4]
    )

    save_github_json(
        WINNER_FILE,
        st.session_state.winner_history
    )

# --------------------------------------------------
# DISPLAY WINNER
# --------------------------------------------------

if st.session_state.winner:

    st.success(
        f"🏆 Winner: {st.session_state.winner['name']}"
    )

# --------------------------------------------------
# LAST 4 WINNERS
# --------------------------------------------------

st.markdown("---")

st.subheader(
    "🏅 Last 4 Winners"
)

if st.session_state.winner_history:

    for i, item in enumerate(
        st.session_state.winner_history,
        start=1
    ):

        st.write(
            f"{i}. 🏆 {item['name']} | 📅 {item['date']}"
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