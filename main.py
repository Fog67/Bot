from mock_reader import mock_reader
from normalizer import Device, Devices
import asyncio
import json
from datetime import datetime


if __name__ == "__main__":
        for packet in mock_reader():
            print(Devices(packet).to_dictlist())


