#@title a
import re
import os
import copy
import shutil
import ffmpeg
import torch
import librosa
import tempfile
from TTS.api import TTS
from pydub import AudioSegment

class SubToAudio:

  def __init__( self,
                model_name:str=None,
                model_path:str=None,
                config_path:str=None,
                progress_bar:bool=False,
                fairseq_language:str=None,
                **kwargs,
              ):

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if fairseq_language != None and model_name == None:
      model_name = f"tts_models/{fairseq_language}/fairseq/vits"
    if model_name != None and model_path == None:
      try:
        self.apitts = TTS(model_name=model_name, progress_bar=progress_bar, **kwargs).to(device)
      except:
        self.apitts = TTS(model_name, progress_bar=progress_bar, **kwargs).to(device)
    elif model_path != None and model_name == None:
      if config_path == None:
        print("Expecting config_path.json")
      else:
        self.apitts = TTS(model_path=model_path,
                          config_path=config_path,
                          progress_bar=progress_bar,
                          **kwargs).to(device)

  def subtitle(self, file_path:str):
    self.name_path = file_path
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as temp_file:
      temp_filename = temp_file.name
      input_stream = ffmpeg.input(file_path)
      try:
        ffmpeg.output(input_stream, temp_filename, y='-y').run()
      except:
        temp_file.close()
        os.unlink(temp_filename)
      temp_file.close()
      dictionary = self._extract_data_srt(temp_filename)
      os.unlink(temp_filename)
    return dictionary

  def convert_to_audio(self,
                       sub_data:list=None,
                       speaker:str=None,
                       language:str=None,
                       voice_conversion:bool=False,
                       speaker_wav:str=None,
                       output_path:str=None,
                       tempo_mode:str=None,
                       tempo_speed:float=None,
                       tempo_limit:float=None,
                       shift_mode:str=None,
                       shift_limit:int or str=None,
                       save_temp:bool=False,
                       speed:float=None,
                       emotion:str=None,
                       voice_dir:str=None,
                       preset:str=None,
                       num_autoregressive_samples:int=None,
                       diffusion_iterations:int=None,
                       decoder_iterations:int=None,
                       **kwargs,
                      ):

    shift_set = {"right", "left", "interpose", "left-overlap", "interpose-overlap"}
    data =  copy.deepcopy(sub_data)
    convert_param = {}
    common_param = {"language":language,
                    "speaker_wav":speaker_wav
                    }
    vcfalse_param = { "voice_dir":voice_dir,
                      "preset":preset,
                      "num_autoregressive_samples": num_autoregressive_samples,
                      "diffusion_iterations": diffusion_iterations,
                      "decoder_iterations": decoder_iterations,
                      "preset":preset,
                      "emotion":emotion,
                      "speed":speed,
                      "speaker":speaker,
                      }

    try:
      if speaker == None:
        vcfalse_param['speaker'] = self.apitts.speakers[0]
        print(f"speaker is None, using '{vcfalse_param['speaker']}' as default")
      if language == None:
        common_param['language'] = self.apitts.languages[0]
        print(f"Language is None, using '{common_param['language']}' as default")
    except:
      pass

    if output_path == None:
      output_path = os.path.splitext(self.name_path)[0] + ".wav"
    elif os.path.splitext(output_path)[1] != ".wav":
      output_path += ".wav"

    if tempo_mode == "all":
      if tempo_speed is None or not isinstance(tempo_speed, float):
        tempo_speed = 1.2
        print(f"tempo_speed speed is not Float")
        print(f"tempo_speed change to default value '{tempo_speed}'")

    if voice_conversion:
      convert_param = {**common_param}
      tts_method = self.apitts.tts_with_vc_to_file
    else:
      convert_param = {**common_param,**vcfalse_param,**kwargs}
      tts_method = self.apitts.tts_to_file

    with tempfile.TemporaryDirectory() as temp_folder:
      print("Temporary folder:", temp_folder)

      for entry_data in data:
        audio_path = f"{temp_folder}/{entry_data['audio_name']}"
        tts_method(f"{entry_data['text']}",file_path=audio_path,**convert_param)

        if tempo_mode == "all":
          self._tempo(mode=tempo_mode,audiopath=audio_path,
                      tempospeed = tempo_speed)

        elif tempo_mode == "overflow" or tempo_mode == "precise":
          audio_length = self._audio_length(audio_path)
          subt_time = entry_data['sub_time']
          if audio_length > subt_time:
            if tempo_mode == "overflow":
              sub_time = subt_time
            elif tempo_mode == "precise":
              sub_time = entry_data['end_time'] - entry_data['start_time']
              shift_mode = None
            self._tempo(mode=tempo_mode,
                        audiopath = audio_path,
                        audiolength=audio_length,
                        subtime=sub_time,
                        tempolimit=tempo_limit)

        audio_length = self._audio_length(audio_path)
        entry_data['audio_length'] = audio_length

      if shift_mode in shift_set:
        try:
          if shift_limit[-1] == "s":
            shift_limit = int(float(shift_limit[:-1]) * 1000)
        except:
          shift_limit = None
        data = self._shifter(data=data, mode=shift_mode, shiftlimit=shift_limit)

      end_time = data[-1]['end_time']
      base_duration = end_time + 10000
      blank_base_audio = AudioSegment.silent(duration=base_duration)

      for entry_data in data:
        audio_path = f"{temp_folder}/{entry_data['audio_name']}"
        position = entry_data['start_time']
        overlay_audio = AudioSegment.from_file(audio_path)
        blank_base_audio = blank_base_audio.overlay(overlay_audio, position=position)

      blank_base_audio.export(output_path, format="wav")

      if save_temp:
        new_folder_name = f"{os.path.splitext(self.name_path)[0]}_{os.path.basename(os.path.normpath(temp_folder))}"
        self._move_tempaudio(temp_folder, new_folder_name)

  def _tempo(self,
             mode:str,
             audiopath:str,
             tempospeed:float=None,
             audiolength:int=None,
             subtime:int=None,
             tempolimit:float=None,
            ):

    if mode == "all":
      atempo = tempospeed
    if mode == "overflow":
      atempo = audiolength / subtime
      if tempolimit is not None and isinstance(tempolimit, float):
        if atempo > tempolimit:
          atempo = tempolimit
    if mode == "precise":
      atempo = audiolength / subtime

    atempo = round(atempo, 2)
    audio_out = audiopath+"temp.wav"
    print(f" > atempo: {atempo}")
    ffmpeg_command = (ffmpeg.input(audiopath).filter('atempo',atempo).output(audio_out))
    try:
      ffmpeg_command.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e
    os.rename(audiopath, audiopath + "original.wav")
    os.rename(audio_out, audiopath)

  def _audio_length(self, audio_path):
    return int(round(librosa.get_duration(path=audio_path),3) * 1000)

  def _shifter(self, data:list, mode:str, shiftlimit:int=None):

    if mode == "right":
      for i in range(len(data)):
        if data[i]['audio_length'] > data[i]['sub_time']:
          shift_time = data[i]['audio_length'] - data[i]['sub_time']
          if isinstance(shiftlimit, int) and shiftlimit < shift_time:
            shift_time = shiftlimit
          if i + 1 < len(data):
            data[i+1]['start_time'] += shift_time
            data[i+1]['end_time'] += shift_time
            data[i+1]['sub_time'] -= shift_time

    elif "left" in mode or mode == "left":
      data = data[::-1]
      for i in range(len(data)):
        if data[i]['audio_length'] > data[i]['sub_time']:
          shift_time = data[i]['audio_length'] - data[i]['sub_time']
          if isinstance(shiftlimit, int) and shiftlimit < shift_time:
            shift_time = shiftlimit
          data[i]['start_time'] -= shift_time
          data[i]['end_time'] -= shift_time
          if "-overlap" not in mode:
            if i + 1 < len(data):
              data[i+1]['sub_time'] -= shift_time
      data = data[::-1]

    elif "interpose" in mode or mode == "interpose":
      for i in range(len(data)):
        if data[i]['audio_length'] > data[i]['sub_time']:
          shift_time = int((data[i]['audio_length'] - data[i]['sub_time']) / 2)
          data[i]['start_time'] -= shift_time
          data[i]['end_time'] -= shift_time
          if "-overlap" not in mode:      
            if i + 1 < len(data):
              data[i+1]['start_time'] += shift_time
              data[i+1]['end_time'] += shift_time
              data[i+1]['sub_time'] -= shift_time
            if i - 1 > 0:
              data[i-1]['sub_time'] -= shift_time
              if data[i-1]['audio_length'] > data[i-1]['sub_time']:
                data[i-1]['start_time'] -= shift_time
                data[i-1]['end_time'] -= shift_time
    return data  

  def _extract_data_srt(self, file_path):
    subtitle_data = []
    pattern = r'(\d+)\n([\d:,]+) --> ([\d:,]+)\n(.+?)\n\n'

    with open(file_path, 'r', encoding="utf-8") as file:
        file_content = file.read()

    matches = re.findall(pattern, file_content, re.DOTALL)

    for i, match in enumerate(matches):
      entry_number = int(match[0])
      start_time = match[1]
      end_time = match[2]
      text = match[3].strip()
      clean_text = re.sub(r'<.*?>', '', text)
      start_time = self._convert_time_to_intmil(start_time)
      end_time = self._convert_time_to_intmil(end_time)
      if i < len(matches) - 1:
        next_start_time = self._convert_time_to_intmil(matches[i + 1][1])
        sub_time = next_start_time - start_time
      else:
        sub_time = end_time - start_time + 5000
      sub_data = {
          'entry_number': entry_number,
          'start_time': start_time,
          'end_time': end_time,
          'text': clean_text,
          'sub_time': sub_time,
          'audio_name': f"{entry_number}_audio.wav"
      }
      subtitle_data.append(sub_data)
    file.close()
    return subtitle_data

  def _convert_time_to_intmil(self, time):
    time_string = time
    time_string = time_string.replace(":", "").replace(",", "")
    hours = int(time_string[:2])
    minutes = int(time_string[2:4])
    seconds = int(time_string[4:6])
    milliseconds = int(time_string[6:])
    total_milliseconds = (hours * 60 * 60 * 1000) + (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
    return total_milliseconds

  def _move_tempaudio(self, folder_path, new_folder):
    try:
        new_folder_path = os.path.join(os.getcwd(), new_folder)
        os.mkdir(new_folder_path)
        if not os.path.exists(new_folder_path):
          os.mkdir(new_folder_path)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                shutil.move(item_path, new_folder)
        print("Temp files moved successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")

  def speakers(self):
    return self.apitts.speakers()

  def languages(self):
    return self.apitts.languages()

  def coqui_model(self):
    return self.TTS().list_models()
