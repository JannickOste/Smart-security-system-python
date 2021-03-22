import os
import re
from datetime import datetime

import numpy
from typing import Union

import cv2
import face_recognition


class Webcam:
    # Target camera and current rendered frames by camera
    target_id = -1

    __target = None
    __ret, __frame = None, None
    __workers = []

    # Write process if valid location is specified
    __write_process = None, None
    __faceTracking = False

    __config = None

    # Initiation procedure
    def __init__(self, config,  target_id: int = 0) -> None:
        """
        Initiate the camera capture and assign id for external access
        """
        self.__config = config
        self.target_id = target_id
        self.__target = cv2.VideoCapture(self.target_id, cv2.CAP_DSHOW)

    def start(self, render: bool = True) -> None:
        """
        Currently doesnt do a lot except for starting render,
        placeholder if more startup functionality is required.
        """

        if render:
            self.__render(self.__config.GetFilePath("video_output_location"))

    def __render(self, output_location: str) -> None:
        """
        Initiate camera frame
        :param output_location:
        :return:
        """

        write_process = None
        encodings = self.__config.known_encodings
        while self.__target.isOpened():
            # Read and assign current frame.
            render, frame = self.__target.read()

            if self.__faceTracking:
                write_process = self.__faceTrack(frame, encodings, write_process, output_location)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close()
            elif render:
                cv2.imshow(f'Camera {self.target_id}', frame)
                if write_process is not None:
                    write_process.write(frame)

    def __faceTrack(self, frame, encodings, write_process, output_location):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        found_names = []

        try:

            for encoding in face_recognition.face_encodings(rgb_frame, locations):
                name = None
                match = None
                for set_name in encodings.keys():
                    match = face_recognition.compare_faces(encodings[set_name], encoding, tolerance=0.50)
                    if match[0]:
                        name = set_name
                        break

                found_names.append(name)
        except Exception as e:
            print(e)
        try:
            for (top, right, bottom, left), name in zip(locations, found_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 0), 2)
                cv2.rectangle(frame, (left, bottom), (right, bottom), (0, 0, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
        except Exception as e:
            print(e)

        if locations and write_process is None:
            try:
                day_dir, timestamp = f'{re.sub(r"[-.:]", "_", str(datetime.now()))}'.split(" ")
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(output_location)))
                if day_dir not in os.listdir(base_dir):
                    os.mkdir(os.path.dirname(output_location.format(directory=day_dir, timestamp="")))

                write_process = cv2.VideoWriter(output_location.format(directory=day_dir, timestamp=timestamp),
                                                                      cv2.VideoWriter_fourcc(*'XVID'), 30.0, (640, 480))
            except Exception as e:
                print(e)
        elif len(locations) == 0 and write_process is not None:
            write_process = None

        return write_process

    # Get current device output
    def getOutput(self) -> Union:
        """
        Get current rendered frame
        :return: frame received, numpy data
        """
        return self.__target.read()

    def setFrame(self, new_frame: numpy.ndarray) -> None:
        """
        Override current rendered frame
        """
        self.__frame = new_frame

    # Webcam is writing or showing.
    def isActive(self) -> bool:
        """
        Check or the camera capture is opened
        :return: camera is active
        """
        return self.__target.isOpened()

    def toggleTracking(self) -> None:
        """
        Set face tracking true/false inverse of the current state
        :return:
        """
        self.__faceTracking = not self.__faceTracking

    # Close the webcam renderer.
    def close(self) -> None:
        """
        Release necessary processes
        :return:
        """
        self.__write_process.release()
        self.__target.release()
        cv2.destroyAllWindows()
