# Subtitle to Audio
Generate audio from any subtitle file using coqui-ai TTS.

## Dependencies
[ffmpeg](https://ffmpeg.org/), [pydub](https://github.com/jiaaro/pydub), [librosa](https://github.com/librosa/librosa), [Coqui-ai TTS](https://github.com/coqui-ai/TTS/)


## Installation

```bash
pip install git+https://github.com/bnsantoso/sub-to-audio
```
ffmpeg on linux
```bash
apt-get install ffmpeg
```
## Example usage

Basic use is very similiar to [Coqui-ai TTS](https://github.com/coqui-ai/TTS/), you can check their documentation.

```python
from subtoaudio import SubToAudio

#using fairseq english speaker model as default, and will outputing "output.wav" in current directory.
sub = SubToAudio(gpu=True)
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle)

#you can chose 1100 different language using fairseq model
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

#by default is using "speaker=tts.speakers[0]/None, language=tts.languages[0]/None, speaker_wav=None"
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/your_tts")
subtitle = sub.subtitle("yoursubtitle.srt")
sub.convert_to_audio(data=subtitle, language="en", speaker="speakername", speaker_wav="your/path/speaker.wav", output_path="subtitle.wav")

```


## TODO

- [ ] Multiple speaker
