# coding: utf-8

"""
    Install RPIO: https://pythonhosted.org/RPIO/index.html
"""
import GPIO
import time
import logging
from am2320_driver import AM2320

SLEEP_MS = 5000
FOGGER_MS = 500


TARGET_HUMI = 80
TARGET_TEMP = 20

SENSOR_1_BUS = 0x00             # PIN 3
SENSOR_2_BUS = 0x01             # PIN 5
SENSOR_3_BUS = 0x02             # PIN 27
SENSOR_4_BUS = 0x02             # PIN 28

FOG_BUS = 0x00                  # PIN
RIDGE_1_FAN_BUS = 0x00          # PIN
RIDGE_2_FAN_BUS = 0x00          # PIN

BASEMENT_1_FAN_BUS = 0x02       # PIN
BASEMENT_2_FAN_BUS = 0x02       # PIN

RECIRCULATION_1_FAN_BUS = 0x00  # PIN
RECIRCULATION_2_FAN_BUS = 0x00  # PIN
RECIRCULATION_3_FAN_BUS = 0x00  # PIN
RECIRCULATION_4_FAN_BUS = 0x00  # PIN


class Fan(object):
    """ Класс управления вентиляторами """

    def enable(self):
        """ Включение вентилятора """
        pass

    def disable(self):
        """ Отключение вентилятора """
        pass

    def adjust(self):
        """ Подгон мощности (плюс / минус)"""
        pass


class ExtractionRidgeFan(Fan):
    """ Управление коньковым вытяжным вентилятором (понижение температуры) """
    pass


class ExtractionBasementFan(Fan):
    """ Управление вентилятором под кассетами (понижение влажности) """
    pass


class CuttingsGreenhouse(object):
    """ Управление теплицей """
    sensors: list[AM2320] = []
    humi_list: list[float] = []
    temp_list: list[float] = []

    def __init__(self):
        """ """
        self.sensors = [
            AM2320(SENSOR_1_BUS),
            AM2320(SENSOR_2_BUS),
            AM2320(SENSOR_3_BUS),
        ]

        self.relay_fog = []
        self.relay_ridge_1_fan = []
        self.relay_ridge_2_fan = []

    @property
    def actual_humi(self) -> float:
        return sum(self.humi_list) / len(self.humi_list)

    @property
    def actual_temp(self) -> float:
        return sum(self.temp_list) / len(self.temp_list)

    def run(self):
        """ Работа по череночнику:
            - чтение сенсоров
            - коррекция ШИМ вентиляторов
        """
        while True:
            self.update_sensors()
            self.update_ridge_fun()
            self.update_basement_fun()
            self.update_fog()

    def update_sensors(self):
        """ Чтение обновленных данных из череночника """
        self.humi_list = []
        self.temp_list = []

        for idx, sensor in enumerate(self.sensors):
            hum, temp = self.read_sensor(idx)
            self.humi_list.append(hum)
            self.temp_list.append(temp)

    def update_fog(self):
        """ Включить туман, выключить туман и спать N секунд """
        GPIO.output(FOG_BUS, GPIO.HIGH)
        time.sleep(FOGGER_MS / 1000)
        GPIO.output(FOG_BUS, GPIO.LOW)
        time.sleep(SLEEP_MS)

    def read_sensor(self, idx):
        """ Новые данные от датчика по влажности и температуре """
        return self.sensors[idx].get_humi_temp()

    def update_ridge_fun(self):
        pass

    def update_basement_fun(self):
        if self.actual_humi < TARGET_HUMI:
            logger.info(f"Target humi > {self.actual_humi}. Disable basement fans")
            return



if __name__ == '__main__':
    logger = logging.Logger()

    greenhouse = CuttingsGreenhouse()
    greenhouse.run()

