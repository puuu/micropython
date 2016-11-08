# MicroPython SH1106 OLED driver, I2C and SPI interfaces

from micropython import const
from ssd1306 import SSD1306_I2C, SSD1306_SPI

SET_PAGE_ADDR = const(0xB0)
LOW_COLUMN_ADDR = const(0x00)
HIGH_COLUMN_ADDR = const(0x10)

class SH1106():
    def show(self):
        for page in range(self.height // 8):
            self.write_cmd(SET_PAGE_ADDR | page)
            self.write_cmd(LOW_COLUMN_ADDR | 2)
            self.write_cmd(HIGH_COLUMN_ADDR | 0)
            self.write_data(self.buffer[self.width*page:self.width*page+self.width])


class SH1106_I2C(SH1106, SSD1306_I2C):
    pass


class SH1106_SPI(SH1106, SSD1306_SPI):
    pass
