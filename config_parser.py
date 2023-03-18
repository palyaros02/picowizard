import configparser, os


class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__(
            delimiters=('='),
            comment_prefixes=('#'),
            interpolation=configparser.ExtendedInterpolation(),
        )
        self.read('config.cfg', encoding="utf8")

    def reload(self):
        self.read('config.cfg', encoding="utf8")

    def save(self):
        with open('config.cfg', 'w') as configfile:
            self.write(configfile)

    def get_root(self):
        return os.path.dirname(os.path.abspath(__file__))

config = Config()

# FIXME: This is a temporary solution
firmware = {
    'pico4': {
        'oem': {
            'cn': {
                '5.3.1' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.3.1-202301051635-RELEASE-user-phoenix-b2669-c435f2dfde.zip',
                '5.4.0' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.4.0-202302082133-RELEASE-user-phoenix-b3033-575cb027b3.zip',
            },
            'gl': {
                '5.2.7' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/5.2.7-202212020445-RELEASE-user-phoenix-b2122-a15f46c085.zip',
                '5.3.1' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/5.3.1-202301051855-RELEASE-user-phoenix-b2672-e5008f4620.zip',
                '5.3.2' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/5.3.2-202301071817-RELEASE-user-phoenix-b2705-0d2c0cb6ec.zip',
                '5.4.0' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/5.4.0-202302171231-RELEASE-user-phoenix-b3159-21724b5b8e.zip',
            },
        },
        'non_oem': {
            'cn': {'5.4.0' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.4.0-202302091032-RELEASE-user-phoenix-b3046-e076814e50.zip',},
            'gl': {
                '5.2.7' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/non_oem/5.2.7-202212020323-RELEASE-user-phoenix-b2119-09638d5e07.zip',
                '5.3.2' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/non_oem/5.3.2-202301071642-RELEASE-user-phoenix-b2704-ae2fa5f1b3.zip',
                '5.3.1' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/non_oem/5.3.1-202301051632-RELEASE-user-phoenix-b2667-6c560f9e2b.zip',
                '5.4.0' : 'https://mirror.lewd.wtf/archive/picoxr/firmware/pico4/global/non_oem/5.4.0-202302171557-RELEASE-user-phoenix-b3162-3d2f0dbe1b.zip',
            },
        },
    },
    'pico3': {
        'cn': {
            '4.9.3' : 'https://alistatic.pui.picovr.com/4.9.3-202209091733-RELEASE-user-neo3-b1759-7384689bc9.zip',
            '5.2.2' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.2.2-202212020144-RELEASE-user-neo3-b2405-e2f0482a98.zip',
            '5.2.3' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.2.3-202212090601-RELEASE-user-neo3-b2475-c8012b4f3e.zip',
            '5.3.1' : 'https://lf-stone-iot-va.dlpicovr.com/obj/stone-iot-us/ota-out/pico_oversea_rls_neo3-mol-5.3.3-20230103-SEKSA.falconcv3apollo-user/202301040122/5.3.1.0-202301032255-RELEASE-user-neo3-b756-6de3f4fa71.zip',
            '5.3.4-beta' : 'https://lf-iot-ota.picovr.com/obj/iot-ota/5.3.4-202301032204-RELEASE-user-neo3-b2760-35084bb960.zip',
        },
        'gl': {
            '4.8.0' : 'https://static.us-pui.picovr.com/4.8.0.0-202210141246-RELEASE-user-neo3-b570-4133044097.zip',
             '5.3.1' : 'https://lf-stone-iot-va.dlpicovr.com/obj/stone-iot-us/ota-out/pico_oversea_rls_neo3-mol-5.3.3-20230103-SEKSA.falconcv3apollo-user/202301040122/5.3.1.0-202301032255-RELEASE-user-neo3-b756-6de3f4fa71.zip',
        },
    },
}