import os
import torch
import time
import uuid
from OpenVoice.openvoice import se_extractor
from OpenVoice.openvoice.api import ToneColorConverter
from melo.api import TTS

from fastapi import FastAPI, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

device = "cuda:0" if torch.cuda.is_available() else "cpu"
ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 应用启动时加载模型
    ckpt_converter = 'OpenVoice/checkpoints_v2/converter'
    tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

    tts_models = {
        lang: TTS(language=lang, device=device)
        for lang in ['ZH', 'EN_NEWEST', 'EN', 'ES', 'FR', 'JP', 'KR']
    }

    ml_models["tone_color_converter"] = tone_color_converter
    ml_models["tts_models"] = tts_models

    yield

    # 应用关闭时释放资源
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


async def generate_voice(text: str, reference_speaker: str, speed: float, language: str) -> str:
    output_dir = 'outputs_v2'
    os.makedirs(output_dir, exist_ok=True)

    tone_color_converter = ml_models.get("tone_color_converter")
    tts_models = ml_models.get("tts_models")

    if not tone_color_converter or not tts_models:
        return None

    target_se, _ = se_extractor.get_se(reference_speaker, tone_color_converter, vad=True)
    src_path = f'{output_dir}/tmp_{uuid.uuid4().hex}.wav'

    model = tts_models.get(language)
    if not model:
        print(f"Error: TTS model for language '{language}' not found.")
        return None

    speaker_ids = model.hps.data.spk2id
    for speaker_key, speaker_id in speaker_ids.items():
        speaker_key = speaker_key.lower().replace('_', '-')
        source_se = torch.load(f'OpenVoice/checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=device)

        # Ensure model's method is async
        if not hasattr(model, 'tts_to_file'):
            print("Error: TTS model does not have 'tts_to_file' method.")
            return None

        model.tts_to_file(text, speaker_id, src_path, speed=speed)

        save_path = f'{output_dir}/output_{int(time.time())}_{speaker_key}.wav'
        encode_message = "@lin"
        tone_color_converter.convert(
            audio_src_path=src_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=save_path,
            message=encode_message
        )
        return save_path
    return None


async def cleanup_file(file_path: str):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {file_path}. Error: {e}")


@app.post("/text2voice")
async def text2voice(
        background_tasks: BackgroundTasks,
        text: str = Form(..., description="要转换的文本"),
        speaker: UploadFile = File(..., description="声音文件"),
        speed: float = Form(1.0, description="语速"),
        language: str = Form('ZH', description="语言")
):
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    reference_speaker = tmp_dir / f'{uuid.uuid4().hex}_{speaker.filename}'

    with open(reference_speaker, 'wb') as f:
        f.write(await speaker.read())

    file_path = await generate_voice(text, str(reference_speaker), speed=speed, language=language)

    background_tasks.add_task(cleanup_file, str(reference_speaker))
    if file_path:
        background_tasks.add_task(cleanup_file, file_path)
        return FileResponse(file_path)
    else:
        return {"message": "转换失败"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
