import time
import framebuf
from machine import Pin, SPI


# 1.5 inch display pins
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

class OLED_1inch3(framebuf.FrameBuffer):
    # Built-in buttons on display
    keyA = Pin(15,Pin.IN,Pin.PULL_UP)
    keyB = Pin(17,Pin.IN,Pin.PULL_UP)
    
    def __init__(self):
        self.width = 128
        self.height = 64
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,2000_000)
        self.spi = SPI(1,20000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        self.initDisplay()
        
        self.white =   0xffff
        self.black =   0x0000
        
    def writeCMD(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def writeData(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def initDisplay(self):
        """Initialize display"""  
        self.rst(1)
        time.sleep(0.001)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        
        self.writeCMD(0xAE)    # turn off OLED display

        self.writeCMD(0x00)    # set lower column address
        self.writeCMD(0x10)    # set higher column address 

        self.writeCMD(0xB0)    # set page address 
      
        self.writeCMD(0xdc)    # set display start line 
        self.writeCMD(0x00) 
        self.writeCMD(0x81)    # contract control 
        self.writeCMD(0x6f)    # 128
        self.writeCMD(0x21)    # Set Memory addressing mode (0x20/0x21)
    
        self.writeCMD(0xa0)    # set segment remap 
        self.writeCMD(0xc0)    # com scan direction
        self.writeCMD(0xa4)    # Disable Entire Display On (0xA4/0xA5) 

        self.writeCMD(0xa6)    # normal / reverse
        self.writeCMD(0xa8)    # multiplex ratio 
        self.writeCMD(0x3f)    # duty = 1/64
  
        self.writeCMD(0xd3)    # set display offset 
        self.writeCMD(0x60)

        self.writeCMD(0xd5)    # set osc division 
        self.writeCMD(0x41)
    
        self.writeCMD(0xd9)    # set pre-charge period
        self.writeCMD(0x22)   

        self.writeCMD(0xdb)    # set vcomh 
        self.writeCMD(0x35)  
    
        self.writeCMD(0xad)    # set charge pump enable 
        self.writeCMD(0x8a)    # set DC-DC enable (a=0:disable; a=1:enable)
        self.writeCMD(0XAF)
    
    def clearDisplay(self):
        self.fill(self.black)
        self.show()
        
    def show(self):
        self.writeCMD(0xb0)
        for page in range(0,64):
            self.column = 63 - page              
            self.writeCMD(0x00 + (self.column & 0x0f))
            self.writeCMD(0x10 + (self.column >> 4))
            for num in range(0,16):
                self.writeData(self.buffer[page*16+num])