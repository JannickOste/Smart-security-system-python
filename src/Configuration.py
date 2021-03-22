import os, face_recognition
from xml.dom import minidom

import cv2


class Configuration:
    """
        Handler for XML configuration file and necessary assets
    """
    __config_path = f"/"
    __config = None
    __known_encodings = {}

    def __init__(self):
        print("Loading assets...")
        self.__config = minidom.parse(os.path.join(self.__AssetPath(), "configuration.xml"))

        face_dir = self.GetFilePath("know_face_encodings")
        for directory in [directory for directory in os.listdir(face_dir) if os.path.isdir(os.path.join(face_dir, directory))]:
            self.__known_encodings[directory] = []
            for file in os.listdir(os.path.join(face_dir, directory)):
                image = cv2.cvtColor(face_recognition.load_image_file(os.path.join(face_dir, directory, file)), cv2.COLOR_BGR2RGB)
                encoding = face_recognition.face_encodings(image)

                if encoding:
                    self.__known_encodings[directory].append(encoding[0])

    @property
    def projectRoot(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))[:-4]

    def __AssetPath(self) -> str:
        return f"{self.projectRoot}\\Assets"

    def Get(self, key: str) -> str:
        for val in self.__config.getElementsByTagName("value"):
            if key == val.attributes["name"].value:
                return val.attributes["value"].value

        return ""

    def GetFilePath(self, key: str) -> str:
        for val in self.__config.getElementsByTagName("path"):
            if key == val.attributes["name"].value:
                return f"{self.__AssetPath()}\\{val.attributes['value'].value}".replace("/", "\\")

        return ""

    def enabledModules(self):
        for module_element in self.__config.getElementsByTagName("module"):
            if module_element.attributes["enabled"].value.lower() == "true":
                yield module_element.attributes["name"].value

    @property
    def known_encodings(self):
        return self.__known_encodings
