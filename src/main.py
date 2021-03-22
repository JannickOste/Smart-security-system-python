from typing import Union

import src.devices, src.classes
from concurrent.futures import ThreadPoolExecutor

from src import Configuration

"""
    @Todos: 
    - Add face recognition
    - Add automated camera detection
"""


class Main:
    devices: int = 2
    __max_devices = 10

    __modules: dict = {}
    __device_threads: Union = []
    __worker_threads: Union = []

    __audio: src.classes.SpeechHandler = None
    __video: src.classes.CameraHandler = None
    __config: src.Configuration = Configuration.Configuration()

    def __init__(self) -> None:
        """
        Assign all device objects
        """

        self.__audio = src.classes.SpeechHandler(self.__config)
        self.__video = src.classes.CameraHandler(self.__config)
        self.__start()

    def __start(self) -> None:
        """
        Start processing camera and audio input
        """

        print(f"Found {self.__video.connected_devices} video device(s)")

        # self.audio.output("Starting processing")
        with ThreadPoolExecutor() as executor:
            for device in self.__video.devices:
                self.__device_threads.append(executor.submit(device.start))

            self.__worker_threads.append(executor.submit(self.__update))

    def __update(self):
        print("Asking question")
        try:
            self.__audio.askQuestion("System enabled sir, do you wish to enable face tracking?",
                                     "Enabling face tracking",
                                     "Sorry sir, i failed to understand you, i will just leave it as is",
                                     ["yes", "oke"], getattr(self.__video, "toggleTracking"))

        except Exception as e:
            print(e)

    # while any([not thread.done() for thread in self.__device_threads]):
    #     print("Running")


if __name__ == "__main__":
    Main()
