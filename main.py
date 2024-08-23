import streamlit as st

pg = st.navigation([
    st.Page("coqui.py", title="Coqui TTS", icon="🐸"),
    st.Page("openvoice.py", title="OpenVoice TTS", icon="🔥"),
    st.Page("recording.py", title="录音机", icon="🎙️")
])
pg.run()
