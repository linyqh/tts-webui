import streamlit as st
from st_audiorec import st_audiorec

st.text("阅读下面内容，并录制一段声音")
st.text("故事发生在神秘的大海上，这是一段充满了海盗和宝藏的奇幻旅程。")

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')
