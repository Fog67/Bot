from mock_reader import mock_reader
from normalizer import Device
import asyncio
import json
from datetime import datetime


if __name__ == "__main__":
    async def test():
        async for packet in mock_reader():
            print(Device(**packet))


    asyncio.run(test())