import time
from Exceptions import SimEngineConnectionError, SimEngineInjectionError

import win32com.client
from pywintypes import com_error


class SimEngineInterface:
    def __init__(self):
        self.is_connected = False
        self.last_error = ''
        try:
            self.sim_stu_instance = win32com.client.Dispatch("SimControl.SimScript")
            self.is_connected = True

            self.unapply_values()

        except com_error:
            raise SimEngineConnectionError('SimControl.dll was not found.')

    def __del__(self):
        if self.is_connected is True:
            self.set_noise(False)
            self.unapply_values_on_exit()
            self.unapply_values()

    def set_noise(self, enable: bool):
        self.__check_connected()
        self.sim_stu_instance.NoiseEnable(enable)
        self.__check_error()

    def unapply_values(self):
        self.__check_connected()
        self.sim_stu_instance.UnapplyAll()
        self.__check_error()

    def unapply_values_on_exit(self):
        self.__check_connected()
        self.sim_stu_instance.UnapplyAllOnExit()
        self.__check_error()

    def inject_value(self, label: str, unit: str, value: str):
        self.__check_connected()
        self.sim_stu_instance.SetElementValue(label, unit, value)
        self.__check_error()

    def inject_noise_steps(self, label: str, unit: str, value: str, frequency: str, start_value: str, end_value: str):
        self.__check_connected()
        self.sim_stu_instance.NoiseSteps(label, unit, value, frequency, start_value, end_value, 0, 1)
        self.__check_error()

    def inject_noise_sine(self, label: str, unit: str, bias: str, amplitude: str, frequency: str):
        self.__check_connected()
        self.sim_stu_instance.NoiseSine(label, unit, bias, amplitude, frequency, 0, 1)
        self.__check_error()

    def inject_noise_constant(self, label: str, unit: str, value: str, duration: int, override: int):
        self.__check_connected()
        self.sim_stu_instance.NoiseConstant(label, unit, value, duration, override)
        time.sleep(duration / 1000.0)
        self.__check_error()

    def inject_noise_pulse(self, label: str, unit: str, first_value: str, first_duration: int, second_value: str, second_duration: int, repetitions: int):
        self.__check_connected()
        self.sim_stu_instance.NoisePulse(label, unit, first_value, first_duration, second_value, second_duration, repetitions, 1)
        time.sleep((repetitions * (first_duration + second_duration)) / 1000.0)
        self.__check_error()

    def inject_noise_manhattan(self, label: str, unit: str, values: str, repetitions: int):
        self.__check_connected()

        split_values = values.split(',')
        sleep_count_ms = 0

        for index, item in enumerate(split_values):
            if index == (split_values.__len__()-1):
                break
            if index % 2 != 0:
                try:
                    sleep_count_ms += int(item)
                except ValueError:
                    raise SimEngineInjectionError(f'SimEngine injection error: \"{item}\" must be a number!')

        self.sim_stu_instance.NoiseManhattan(label, unit, values, repetitions, 1)
        self.__check_error()

    def get_element_value(self, label: str, unit: str) -> str:
        self.__check_connected()
        value = self.sim_stu_instance.ElementValue(label, unit)
        self.__check_error()

        return value

    def __check_error(self):
        error_string = self.update_last_error()
        if error_string is not '':
            raise SimEngineInjectionError(f'SimEngine injection error: {error_string}')

    def __check_connected(self):
        if self.is_connected is False:
            raise SimEngineConnectionError('SimEngine interface is not connected.')

    def update_last_error(self) -> str:
        self.last_error = self.sim_stu_instance.LastErrorString
        return self.last_error
