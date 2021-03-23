import os
import re
import imutils
from datetime import datetime

import numpy
from  PIL import Image
from typing import Union

import cv2
import face_recognition

from src.Configuration import Configuration


class Webcam:
    # Target camera and current rendered frames by camera
    target_id: int = -1

    __target: cv2.VideoCapture = None
    __write_process: cv2.VideoWriter = None
    __lastFrame: numpy.ndarray = None
    __lastDetectedTime: datetime = None

    __extractKnownFaces = False

    def __init__(self, target_id: int = 0) -> None:
        """
        Initiate the camera capture and assign id for external access
        """
        self.__lastDetectedTime = datetime.now()
        self.target_id = target_id
        self.__target = cv2.VideoCapture(self.target_id, cv2.CAP_DSHOW)

    def start(self, render: bool = True) -> None:
        """
        Currently doesnt do a lot except for starting render,
        placeholder if more startup functionality is required.
        """

        if render:
            self.__render(Configuration.GetFilePath("video_output_location"))

    def __render(self, output_location: str) -> None:
        """
        Initiate camera frame
        :param output_location:
        :return:
        """

        write_process = None
        encodings = Configuration.known_encodings()
        while self.__target.isOpened():
            # Read and assign current frame.
            render, frame = self.__target.read()

            if self.__lastFrame is None:
                self.__lastFrame = cv2.GaussianBlur(cv2.cvtColor(imutils.resize(frame, width=500), cv2.COLOR_BGR2GRAY), (21, 21), 0)
                continue
            try:
                if self.__isMotion(frame) or ((datetime.now()-self.__lastDetectedTime).seconds < 5):
                    write_process = self.__faceTrack(frame, encodings, write_process, output_location)
            except Exception as e:
                print(e)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close()
            elif render:
                cv2.imshow(f'Camera {self.target_id}', frame)
                if write_process is not None:
                    write_process.write(frame)

    def __isMotion(self, frame) -> bool:
        """
        Motion detection flag, if motion = facetrack
        :param frame: current frame to check
        :return: Frame difference within check
        """
        grayed_frame = cv2.GaussianBlur(cv2.cvtColor(imutils.resize(frame, width=500), cv2.COLOR_BGR2GRAY), (21, 21), 0)
        delta = cv2.absdiff(self.__lastFrame, grayed_frame)
        tresh = cv2.dilate(cv2.threshold(delta, 25,255, cv2.THRESH_BINARY)[1], None , iterations=2)
        contours = imutils.grab_contours(cv2.findContours(tresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE))

        try:
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area and area > 500:
                    continue
                self.__lastFrame = grayed_frame
                return True
        except Exception as e:
            print(e)
        return False

    def __faceTrack(self, frame, encodings, write_process, output_location) -> cv2.VideoWriter:
        """
        Track faces upon a frame
        :param frame: target frame
        :param encodings: known encodings
        :param write_process: (un)active write process
        :param output_location: output for writing process
        :return: updated writing process
        """
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
                    self.__lastDetectedTime = datetime.now()

                found_names.append(name)

        except Exception as e:
            print("Error parsing face name: ", e)

        try:
            for (top, right, bottom, left), name in zip(locations, found_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 0), 2)
                cv2.rectangle(frame, (left, bottom), (right, bottom), (0, 0, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                name = name if name is not None else "Unkown"
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

                if self.__extractKnownFaces:
                    frame_slice = rgb_frame[top:bottom, left:right]
                    file_path = os.path.join(Configuration.GetFilePath("know_face_encodings"), name)
                    if not os.path.exists(file_path):
                        os.mkdir(file_path)

                    Image.fromarray(frame_slice).save(os.path.join(file_path, f"{len(os.listdir(file_path))}.png"))

        except Exception as e:
            print("Error setting face rect: ", e)

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

    # Webcam is writing or showing.
    def isActive(self) -> bool:
        """
        Check or the camera capture is opened
        :return: camera is active
        """
        return self.__target.isOpened()

    # Close the webcam renderer.
    def close(self) -> None:
        """
        Release necessary processes
        :return:
        """
        self.__write_process.release()
        self.__target.release()
        cv2.destroyAllWindows()
