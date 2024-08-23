# Dockerfile文件 说明

## 一、OpenVoice TTS

Dockerfile文件用于构建OpenVoice TTS的Docker镜像， api.py 是OpenVoice TTS的API接口， Dockerfile文件中包含了运行OpenVoice TTS所需的依赖。

直接是使用：docker pull linyq1/openvoice:0.1.0-cuda121
### 构建镜像

```
docker build -t openvoice-tts .
```

## 二、edge TTS
参考项目：https://github.com/linyqh/edge-tts-fastapi

### 构建镜像

```
docker build -t edge-tts .
``` 

## 三、Coqui TTS
参考项目：https://github.com/linyqh/TTS

### 构建镜像

```
docker build -t coqui-tts .
```