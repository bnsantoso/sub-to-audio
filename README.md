# Subtitle to Audio
Subtitle to audio, generate audio from any subtitle file using Coqui-ai TTS and synchronize the audio timing according to subtitle time. 

**Demo :** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bnsantoso/sub-to-audio//blob/main/subtitle_to_audio.ipynb)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bnsantoso)
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

Basic use is very similiar to [Coqui-ai TTS](https://github.com/coqui-ai/TTS/), you can check their [documentation](https://tts.readthedocs.io/en/latest/inference.html) and the [<lang-iso_code>](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html).

**!Note: Use non-overlapping subtitles with an optimal Character per Second / CPS for best result**

```python
from subtoaudio import SubToAudio

#Using the Fairseq English speaker model as the default
#The code will output 'yoursubtitle.wav' in the current directory.
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle)

#you can choose 1100 different language using fairseq model
sub = SubToAudio(language='<lang-iso_code>')
subtitle = sub.subtitle("yoursubtitle.ass")
sub.convert_to_audio(sub_data=subtitle) 

#specify model name
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, output_path="subtitle.wav")

#specify model and config path
sub = SubToAudio(model_path="path/to/your/model.pth" config_path="config/path.json")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle)

#By default, it is using "speaker=tts.speakers[0]/None, 
#language=tts.languages[0]/None, speaker_wav=None
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, language="en", speaker="speakername", speaker_wav="your/path/speaker.wav", output_path="subtitle.wav")

#Save temporary audio to current folder
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, output_path="subtitle.wav", save_temp=True)

```

## Tempo Mode

Use the `tempo_mode` parameter to speed up the audio. There are three tempo modes: 

- `tempo_mode="all"` : This accelerates all audio. Use `tempo_speed=float` to specify the speed.
- `tempo_mode="overflow"` : This accelerates the audio to match the total subtitle duration plus the blank duration before the next subtitle appears. `'tempo_limit'` will limit the speed increase during overflow.
- `tempo_mode="precise"` : This accelerates the audio to match the duration the subtitle appears."


```python
from subtoaudio import SubToAudio

#Speed up tempo or speech rate
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, tempo_mode="all", tempo_speed=1.3)

#Change the tempo or speech rate of all audio files , default is 1.2
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, tempo_mode="all", tempo_speed=1.3)

#Change tempo or speech rate to audio that doesn't match the subtitle duration
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, tempo_mode="overflow")

#Limit tempo speed on the overflow mode 
sub.convert_to_audio(sub_data=subtitle, tempo_mode="overflow", tempo_limit=1.2)

#Match audio length to subtitle duration
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=subtitle, tempo_mode="precise")

```

## Shift Mode

`shift_mode` parameter will shift audio that doesnt match subtitle duration.

- `shift_mode="right"` : Shift audio time to the right and prevent audio overlaping.
- `shift_mode="left"` : Shift audio to the left and prevent audio overlap, but be cautious of limited space on the left side, as some audio may disappear.
- `shift_mode="interpose"` : Shift audio to mid position and prevent right and left of audio overlaping. (Note: This mode can be clunky, so use it cautiously.)
- `shift_mode="left-overlap"` : Shift audio time to the left, allowing overlap.
- `shift_mode="interpose-overlap"` : Shift audio to mid position, allowing overlap.
- `shift_limit=int or "str"` : limit audio shift, use integer for millisecond or string like `2.5s` for second

```python
from subtoaudio import SubToAudio

#shift mode with limit of 2 second to the right.
sub = SubToAudio(languages="vie", gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=sub, tempo_mode="overflow", shift_mode="right", limit_shift="2s")

#shift audio to left position or, time before next subtitle appear
sub = SubToAudio(languages="fra" gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=sub, shift_mode="left-overlap")

#shift to left, and limit shift only 1 sec.
sub = SubToAudio(gpu=False)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(sub_data=sub, shift_mode="left", shift_limit=1000) #1000 = 1s

```

### Citation 
Eren, G., & The Coqui TTS Team. (2021). Coqui TTS (Version 1.4) [Computer software]. https://doi.org/10.5281/zenodo.6334862

