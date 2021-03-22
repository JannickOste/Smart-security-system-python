import time
from typing import Union

from src.devices import Audio


class SpeechHandler:
    io = None

    def __init__(self, config):
        self.io = Audio(config)

    def askQuestion(self, question: str, success: str, failed: str, valid_responses: Union, callback) -> None:
        self.io.setOutput(question)
        response = self.io.getInput()

        print("awaiting response")
        if response in valid_responses:
            print(f"success {response}")
            self.io.setOutput(success)
            callback()
        else:
            print(f"failed {response}")
            self.io.setOutput(failed)