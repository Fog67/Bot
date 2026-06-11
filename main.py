from normalizer import Devices
from mock_reader import mock_reader
from buffer import Manager


def main():

    buffer_manager = Manager(
        host="broker.hivemq.com",
        port=1883,
        topic="my_company/sensors/readings"
    )


    reader = mock_reader()



    for raw_data_batch in reader:
        print("\nПолучен пакет данных ---")


        devices_obj = Devices(data_list=raw_data_batch)
        normalized_data = devices_obj.to_dictlist()
        buffer_manager.publish(normalized_data)




if __name__ == "__main__":

    main()