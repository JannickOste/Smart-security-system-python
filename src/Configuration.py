from concurrent.futures import ThreadPoolExecutor
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

    @classmethod
    def __init__(cls):
        print("Loading assets...")
        cls.__config = minidom.parse(os.path.join(cls.__AssetPath(), "configuration.xml"))

        face_dir = cls.GetFilePath("know_face_encodings")

        for directory in [directory for directory in os.listdir(face_dir) if os.path.isdir(os.path.join(face_dir, directory))]:
            if directory.lower() != "unkown":
                cls.__known_encodings[directory] = []
                failed = 0
                for file in os.listdir(os.path.join(face_dir, directory)):
                    file_path = os.path.join(face_dir, directory, file)
                    image = cv2.cvtColor(face_recognition.load_image_file(file_path), cv2.COLOR_BGR2RGB)
                    encoding = face_recognition.face_encodings(image)

                    if encoding:
                        cls.__known_encodings[directory].append(encoding[0])
                    else:
                        os.remove(file_path)
                        failed += 1

                print(f"[Configuration]: Loaded encodings for the user: {directory} "
                      f"(success: {len(cls.__known_encodings[directory])} / failed: {failed})")

                if failed > 0:
                    print("[Configuration]: Restructuring map")
                    offset = 0
                    for file_id, file in enumerate(os.listdir(os.path.join(face_dir, directory))):
                        while True:
                            try:
                                os.rename(os.path.join(face_dir, directory, file), os.path.join(face_dir, directory, f"{file_id+offset}.png"))
                                break
                            except FileExistsError:
                                offset += 1



    @classmethod
    def projectRoot(cls) -> str:
        return os.path.dirname(os.path.abspath(__file__))[:-4]

    @classmethod
    def __AssetPath(cls) -> str:
        return f"{cls.projectRoot()}\\Assets"

    @classmethod
    def Get(cls, key: str) -> str:
        for val in cls.__config.getElementsByTagName("value"):
            if key == val.attributes["name"].value:
                return val.attributes["value"].value

        return ""

    @classmethod
    def GetFilePath(cls, key: str) -> str:
        for val in cls.__config.getElementsByTagName("path"):
            if key == val.attributes["name"].value:
                return f"{cls.__AssetPath()}\\{val.attributes['value'].value}".replace("/", "\\")

        return ""

    @classmethod
    def enabledModules(cls):
        for module_element in cls.__config.getElementsByTagName("module"):
            if module_element.attributes["enabled"].value.lower() == "true":
                yield module_element.attributes["name"].value

    @classmethod
    def known_encodings(cls):
        return cls.__known_encodings
