import os
import streamlit as st
import requests
from utils import is_valid_url

base_url = os.getenv('OPENVOICE_URL', 'http://127.0.0.1:5000')

st.set_page_config(
    page_title="OpenVoice TTS",
    page_icon="🗣️",
)
# 判断url是否有效
if not is_valid_url(base_url):
    st.error(f"OpenVoice TTS 服务地址无效！地址为：{base_url}")

st.write("# 欢迎使用 OpenVoice TTS ! 🔥")

# 输入字段
text = st.text_area("输入文本",
                    "allow the breath to create space and openness in your heart area. guided by your breath to feel the stretch from your entire body down to your toes.")
speaker_file = st.file_uploader("上传参考音频文件（MP3格式）", type=["mp3"])
speed = st.slider("语速", 0.5, 2.0, 1.0)  # 设置语速范围
language = st.selectbox("语言", ["EN", "ZH"])

# 处理提交
if st.button("生成语音"):
    if speaker_file is not None:
        # 显示等待状态
        with st.spinner("正在发送请求..."):
            # 准备POST请求的文件和数据
            files = {
                'text': (None, text),
                'speaker': (speaker_file.name, speaker_file, 'audio/mpeg'),
                'speed': (None, str(speed)),
                'language': (None, language),
            }

            # 发送POST请求
            response = requests.post(
                url=f'{base_url}/text2voice',
                files=files,
                headers={
                    'accept': 'application/json',
                }
            )

            # 检查请求是否成功
            if response.status_code == 200:
                st.success("请求成功！")
                # 如果返回音频数据，可以直接播放
                st.audio(response.content, format="audio/mpeg")
            else:
                st.error(f"请求失败，状态码: {response.status_code}")
    else:
        st.warning("请上传参考音频文件！")
