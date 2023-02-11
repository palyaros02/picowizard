from .ADB import adb


# if __name__ == '__main__':
#     adb = ADB()
#     def check():
#         print("is_connected", adb.is_connected())
#         print("is_wifi_ready", adb.is_wifi_ready())
#         print("is_wifi", adb.is_wifi())
#         print("is_usb", adb.is_usb())
#         print("Status", adb.get_connection_status())


#     # tests
#     # adb.restart_server()
#     check()
#     print(adb.get_devices_list())
#     adb.connect()
#     check()
#     print(adb.get_device())
#     adb.connect_wifi()
#     check()
#     adb.disconnect_wifi()
#     print(adb.get_devices_list())
#     print(adb.get_device())
#     check()
#     # adb.install_driver()
