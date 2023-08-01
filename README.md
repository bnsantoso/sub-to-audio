[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bnsantoso)

# Subtitle to Audio
Subtitle to audio, generate audio from any subtitle file using Coqui-ai TTS and synchronize the audio timing according to subtitle time.

## Dependencies
[ffmpeg](https://ffmpeg.org/), [pydub](https://github.com/jiaaro/pydub), [librosa](https://github.com/librosa/librosa), [coqui-ai TTS](https://github.com/coqui-ai/TTS/), [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)

## Installation

```bash
pip install git+https://github.com/bnsantoso/sub-to-audio
```
```bash
pip install subtoaudio
```
ffmpeg on linux
```bash
apt-get install ffmpeg
```
## Example usage

Basic use is very similiar to [Coqui-ai TTS](https://github.com/coqui-ai/TTS/), you can check their [documentation](https://tts.readthedocs.io/en/latest/inference.html).

```python
from subtoaudio import SubToAudio

#Using the Fairseq English speaker model as the default, the code will output 'yoursubtitle.wav' in the current directory.
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle)

#you can choose 1100 different language using fairseq model
sub = SubToAudio(language='<lang-iso_code>')
subtitle = sub.subtitle("yoursubtitle.ass")
sub.convert_to_audio(data=subtitle) 

#specify model name
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, output_path="subtitle.wav")

#specify model and config path
sub = SubToAudio(model_path="path/to/your/model.pth" config_path="config/path.json")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle)

#By default, it is using "speaker=tts.speakers[0]/None, language=tts.languages[0]/None, speaker_wav=None"
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, language="en", speaker="speakername", speaker_wav="your/path/speaker.wav", output_path="subtitle.wav")

#Change the tempo or speech rate of all audio files , default is 1.2
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, tempo_mode="all", tempo_speed=1.3)

#Change tempo or speech rate to audio that doesn't match the subtitle duration
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, tempo_mode="overflow")

#Limit tempo speed on the overflow mode 
sub.convert_to_audio(data=subtitle, tempo_mode="overflow", tempo_limit=1.2)

#Save temporary audio to current folder
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, output_path="subtitle.wav", save_temp=True)

```

### Citation 
Eren, G., & The Coqui TTS Team. (2021). Coqui TTS (Version 1.4) [Computer software]. https://doi.org/10.5281/zenodo.6334862

