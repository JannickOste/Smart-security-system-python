from typing import Union

import src


class CameraHandler:

    __devices: Union = []

    def __init__(self):
        for i in range(0, 1):
            self.__devices.append(src.devices.Webcam(target_id=i))

    def toggleTracking(self):
        for device in self.__devices:
            device.toggleTracking()

    @property
    def connected_devices(self):
        return len(self.__devices)

    @property
    def devices(self):
        return self.__devices
