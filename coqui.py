import streamlit as st
import requests
import io
import os
from utils import is_valid_url

base_url = os.getenv('COQUI_BASE_URL', None)

st.set_page_config(
    page_title="Coqui TTS",
    page_icon="👋",
)
# 判断url是否有效
if not is_valid_url(base_url):
    st.error(f"Coqui TTS 服务地址无效！地址为：{base_url if base_url else '未设置'}")

st.write("# 欢迎使用 Coqui TTS !")

st.write("模型只需加载一次")
if st.button("加载模型", key="auto_generate_script"):
    with st.spinner("加载模型..."):
        # 模型加载
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        config_path = "/root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json"
        url = f"{base_url}/load_model?model_name={model_name}&config_path={config_path}"
        payload = {}
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        st.success(response.json().get("message"))


# 输入框
text = st.text_input("文本内容", "故事发生在神秘的大海上，这是一段充满了海盗和宝藏的奇幻旅程。")
speaker_idx = st.text_input("说话人（可选）", "")
language_idx = st.text_input("语言索引", "zh")
speed = st.number_input("语速", value=1.0)
split_sentences = st.checkbox("拆分句子", value=True)

# 文件上传
uploaded_file = st.file_uploader("选择一个 WAV 文件", type=["wav", "mp3"])

# 按钮发送请求
if st.button("开始生成"):
    if uploaded_file is not None:
        # 显示等待状态
        with st.spinner("正在发送请求..."):
            # 设置请求的 URL 和头部信息
            url = f"{base_url}/clone_tts"
            headers = {
                "accept": "application/json"
            }
            # 设置请求的表单数据
            files = {
                "text": (None, text),
                "speaker_idx": (None, speaker_idx),
                "language_idx": (None, language_idx),
                "speed": (None, str(speed)),
                "split_sentences": (None, str(split_sentences).lower()),
                "speaker_wav": (uploaded_file.name, uploaded_file, "audio/wav")
            }
            # 发送 POST 请求
            response = requests.post(url, headers=headers, files=files, stream=True)

            # 处理请求结果
            if response.status_code == 200:
                # 将响应内容作为音频流
                audio_bytes = io.BytesIO(response.content)
                # 播放音频
                st.audio(audio_bytes, format="audio/wav")
            else:
                st.error(f"请求失败，状态码：{response.status_code}")
    else:
        st.warning("请上传一个 WAV 文件！")