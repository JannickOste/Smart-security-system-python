import os
import time
from threading import Thread

import speech_recognition as sr
from gtts import gTTS

import playsound
from os import listdir, path, remove


class Audio:
    """
    Microphone and speaker in/output
    """
    __listener = None
    __output_stack = []
    __phase_time_limit = 0
    __audio_proc = None

    __config = None

    def __init__(self, config) -> None:
        self.__config = config
        """
        Assign the speech recognition object and start the audio handling thread
        """
        self.__listener = sr.Recognizer()
        __audio_proc = Thread(target=self.__outputHandler)
        __audio_proc.start()

        # Remove stragglers to avoid corruption exceptions
        temp_storage_dir = path.dirname(self.__config.GetFilePath("temp_microphone_storage"))
        for file in listdir(temp_storage_dir):
            remove(os.path.join(path.dirname(self.__config.GetFilePath("temp_microphone_storage")), file))

    def getInput(self, phrase_time_limit: float = 5) -> str:
        """
        Get the current recognized sentence withing the set limit
        :param phrase_time_limit: time limit for speech
        :return: recognized sentence
        """
        self.__phase_time_limit = phrase_time_limit

        try:
            with sr.Microphone() as mic:
                parsed_audio = self.__listener.listen(mic, phrase_time_limit=phrase_time_limit)
            print(self.__listener.recognize_google(parsed_audio))
            return self.__listener.recognize_google(parsed_audio)
        except Exception as e:
            print(e)
        print("failed")
        return ""

    def setOutput(self, text: str) -> None:
        """
        Set audio output for handler to speak
        :param text: output text
        :return: None
        """
        self.__output_stack.append(text)
        base_dir = path.dirname(self.__config.GetFilePath("temp_microphone_storage"))
        output_path = self.__config.GetFilePath("temp_microphone_storage").format(audio_id=len([file for file in
                                                                                                listdir(base_dir) if
                                                                                                path.isfile(
                                                                                                    path.join(base_dir,
                                                                                                              file))]))

        language = self.__config.Get("language")
        out = gTTS(text, lang=language)
        out.save(output_path)

    """
        Stack based to avoid intertwining audio
    """

    def __outputHandler(self) -> None:
        """
        Output handling thread
        :return: None
        """
        base_dir = path.dirname(self.__config.GetFilePath("temp_microphone_storage"))

        while True:
            for file in [path.join(base_dir, file) for file in listdir(base_dir) if
                         path.isfile(path.join(base_dir, file))]:
                try:
                    playsound.playsound(file)
                except playsound.PlaysoundException as e:
                    print(f"Playback error: {e}")

                if path.exists(file):
                    try:
                        remove(file)
                    except PermissionError as e:
                        continue

            time.sleep(1)

    @property
    def phrase_time_limit(self):
        return self.__phase_time_limit
