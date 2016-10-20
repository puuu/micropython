# MicroPython SH1106 OLED driver, I2C interfaces

import time
import framebuf


# register definitions
_SET_CONTRAST        = const(0x81)
_SET_ENTIRE_ON       = const(0xa4)
_SET_NORM_INV        = const(0xa6)
_SET_DISP            = const(0xae)
_SET_MEM_ADDR        = const(0x20)
_SET_COL_ADDR        = const(0x21)
#SET_PAGE_ADDR       = const(0x22)
_SET_DISP_START_LINE = const(0x40)
_SET_SEG_REMAP       = const(0xa0)
_SET_MUX_RATIO       = const(0xa8)
_SET_COM_OUT_DIR     = const(0xc0)
_SET_DISP_OFFSET     = const(0xd3)
_SET_COM_PIN_CFG     = const(0xda)
_SET_DISP_CLK_DIV    = const(0xd5)
_SET_PRECHARGE       = const(0xd9)
_SET_VCOM_DESEL      = const(0xdb)
_SET_CHARGE_PUMP     = const(0x8d)

_SET_PAGE_ADDR = const(0xB0)
_LOW_COLUMN_ADDR = const(0x00)
_HIGH_COLUMN_ADDR = const(0x10)

class SH1106_I2C():
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        #super().__init__(width, height, external_vcc)
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer1(self.buffer, self.width, self.height)
        self.poweron()
        self.init_display()

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.temp[0] = self.addr << 1
        self.temp[1] = 0x40 # Co=0, D/C#=1
        self.i2c.start()
        self.i2c.write(self.temp)
        self.i2c.write(buf)
        self.i2c.stop()

    def poweron(self):
        pass

    def init_display(self):
        for cmd in (
            _SET_DISP | 0x00, # off
            # address setting
            _SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            _SET_DISP_START_LINE | 0x00,
            _SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            _SET_MUX_RATIO, self.height - 1,
            _SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            _SET_DISP_OFFSET, 0x00,
            _SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            _SET_DISP_CLK_DIV, 0x80,
            _SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            _SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            _SET_CONTRAST, 0xff, # maximum
            _SET_ENTIRE_ON, # output follows RAM contents
            _SET_NORM_INV, # not inverted
            # charge pump
            _SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            _SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(_SET_DISP | 0x00)

    def contrast(self, contrast):
        self.write_cmd(_SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(_SET_NORM_INV | (invert & 1))

    def show(self):
        for page in range(self.height // 8):
            self.write_cmd(_SET_PAGE_ADDR | page)
            self.write_cmd(_LOW_COLUMN_ADDR | 2)
            self.write_cmd(_HIGH_COLUMN_ADDR | 0)
            self.write_data(self.buffer[
                self.width * page:self.width * page + self.width
            ])

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)
