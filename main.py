import streamlit as st

pg = st.navigation([
    st.Page("apps/coqui.py", title="Coqui TTS", icon="🐸"),
    st.Page("apps/openvoice.py", title="OpenVoice TTS", icon="🔥"),
    st.Page("apps/recording.py", title="录音机", icon="🎙️")
])
pg.run()
