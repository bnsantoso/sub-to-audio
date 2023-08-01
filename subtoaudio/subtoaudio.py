import re
import os
import shutil
import ffmpeg
import librosa
import tempfile
from TTS.api import TTS
from pydub import AudioSegment

class SubToAudio:

  def __init__( self,
                model_name: str = None,
                model_path: str = None,
                config_path: str = None,
                progress_bar: bool = True,
                gpu:bool = False,
                languages:str = "eng"
              ):

    if model_path == None:
      if model_name == None:
        if languages == None:
          languages="eng"
        print("using fairseq model as default")
        print("English is default language")
        model_name = f"tts_models/{languages}/fairseq/vits"
      self.apitts = TTS(model_name=model_name, gpu=gpu, progress_bar=progress_bar)
    else:
      if config_path == None:
        print("Expecting config_path.json")
      else:
        self.apitts = TTS(model_path=model_path, 
                          config_path=config_path, 
                          gpu=gpu, 
                          progress_bar=progress_bar)

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
                       data=None,
                       speaker:str=None,
                       languages:str=None,
                       speaker_wav:str=None,
                       output_path:str=None,
                       tempo_mode:str=None,
                       tempo_speed:float=None,
                       tempo_limit:float=None,
                       save_temp:bool=False,
                      ):
    
    try:
      if speaker == None:
        speaker = self.apitts.speakers[0]
        print(f"speaker is None, using '{speaker}' as default")
      if languages == None:
        languages = self.apitts.languages[0]
        print(f"Language is None, using '{languages}' as default")
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

    with tempfile.TemporaryDirectory() as temp_folder:
      print("Temporary folder:", temp_folder)

      for entry_data in data:
        audio_path = f"{temp_folder}/{entry_data['audio_name']}"
        self.apitts.tts_to_file(f"{entry_data['text']}",
                                file_path=audio_path,
                                speaker=speaker,
                                language=languages,
                                speaker_wav=speaker_wav)
        
        if tempo_mode == "all":
          self._tempo(mode=tempo_mode,audiopath = audio_path, 
                      tempospeed = tempo_speed) 

        elif tempo_mode == "overflow":
          audio_length = self._audio_length(audio_path)
          sub_time = entry_data['sub_time']
          if audio_length > sub_time:
            self._tempo(mode=tempo_mode,
                        audiopath = audio_path, 
                        audiolength=audio_length, 
                        subtime=sub_time,
                        tempolimit=tempo_limit)     

        audio_length = self._audio_length(audio_path)
        entry_data['audio_length'] = audio_length

      for i in range(len(data)):
        if data[i]['audio_length'] > data[i]['sub_time']:
          shift_time = data[i]['audio_length'] - data[i]['sub_time'] + 50
          if i + 1 < len(data):
            data[i+1]['start_time'] += shift_time
            data[i+1]['end_time'] += shift_time
            data[i+1]['sub_time'] -= shift_time
      
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
        new_folder_name = os.path.splitext(self.name_path)[0]
        self._move_tempaudio(temp_folder, new_folder_name)
        pass
  
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

    atempo = round(atempo, 2)
    audio_out = audiopath+"temp.wav"
    print(f"atempo {atempo}")
    ffmpeg_command = (ffmpeg.input(audiopath).filter('atempo',atempo).output(audio_out))
    try:
      ffmpeg_command.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e
    os.remove(audiopath)
    os.rename(audio_out, audiopath)

  def _audio_length(self, audio_path):
    return int(round(librosa.get_duration(path=audio_path),3) * 1000)

  def _extract_data_srt(self, file_path):
    subtitle_data = []
    pattern = r'(\d+)\n([\d:,]+) --> ([\d:,]+)\n(.+?)\n\n'

    with open(file_path, 'r') as file:
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
        audio_time = end_time - start_time + 3000
      sub_data = {
          'entry_number': entry_number,
          'start_time': start_time,
          'end_time': end_time,
          'text': clean_text,
          'sub_time': sub_time,
          'audio_name': f"{entry_number}_audio.wav"
      }
      subtitle_data.append(sub_data)
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
