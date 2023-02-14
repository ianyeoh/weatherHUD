import machine
import network
import oled
import weather
import uasyncio
import queue
import time
import ntp_aedt as aedt


OLED = oled.OLED_1inch3()

# Network connectivity
ssid = ''
password = ''

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:        
        for i in range(3):
            OLED.fill(OLED.black)
            OLED.text('Connecting', 20, 23)
            OLED.text('to WiFi.' + (i*'.'), 20, 33)
            OLED.show()
            time.sleep(0.5)
        
    OLED.fill(OLED.black)
    OLED.text('Connected', 20, 23)
    OLED.text(f'to {ssid}', 20, 33)
    OLED.show()
    time.sleep(1.5)
    OLED.clearDisplay()

def initialise():
    OLED.clearDisplay()
    
    # Connect to WLAN
    connect()
    
    aedt.ntpSyncTime()

    while True:
        try:
            # Fetch weather data
            OLED.fill(OLED.black)
            OLED.text('Fetching', 5, 23)
            OLED.text('weather data...', 5, 33)
            OLED.show()
            data = weather.getWeatherData()
            break
        except OSError:
            continue
    
    OLED.clearDisplay()
    return data

def pgSummary(data): 
    OLED.blit(data['icon'], 0, 0)
    condition = uasyncio.create_task(OLED.scrollText(data['condition'], 0, 42, OLED.width, 5))
    OLED.text(f'{data['location'].upper()}', 48, 6)
    OLED.text('F{:2d} |C{:2d}'.format(data['temp_c'], data['pico_temp_c']), 48, 15)
    OLED.ellipse(76, 16, 2, 2, OLED.white)
    OLED.ellipse(116, 16, 2, 2, OLED.white)
    OLED.text('H{:2d}%|{:d}mm'.format(data['humidity'], data['precip_mm']), 48, 25)
    
    return [condition]
    
def pgTemperature(data):
    OLED.blit(weather.thermometer, 0, 6)
    OLED.text('TEMP', 42, 6)
    OLED.text(f'Out|{data['temp_c']}', 42, 18)
    OLED.ellipse(93, 20, 2, 2, OLED.white)
    OLED.text(f'In |{data['pico_temp_c']}', 42, 28)
    OLED.ellipse(93, 30, 2, 2, OLED.white)
    OLED.text(f'FL |{data['feelslike_c']}', 42, 38)
    OLED.ellipse(93, 40, 2, 2, OLED.white)
    return []
    
def pgWind(data):
    OLED.blit(weather.wind, 0, 8)
    OLED.text('WIND', 44, 12)
    OLED.text(f'Speed|Dir', 44, 24)
    OLED.text('{:2d}kph|{:s}'.format(data['wind_kph'], 'N'), 44, 34)
    return []
    
def pgRain(data):
    OLED.blit(weather.raindrop, 0, 6)
    OLED.text('RAIN', 44, 8)
    OLED.text(f'{data['precip_mm']}mm/h', 44, 18)
    OLED.text('HUMIDITY', 44, 28)
    OLED.text(f'{data['humidity']}%', 44, 38)
    return []
    
def pgFooter():
    OLED.rect(0, 52, 128, 12, OLED.black, True)
    OLED.hline(0, 52, 128, OLED.white)
    OLED.hline(0, 53, 128, OLED.white)
    OLED.text(f'{aedt.getTime()} {aedt.getDate()}', 0, 56)
    return []

def pgNumber(pg, pg_len):
    OLED.text(f'{pg}/{pg_len}', 104, 0)

async def updateFooter(delay):
    while True:
        pgFooter()
        OLED.show()
        await uasyncio.sleep(delay)

# Coroutine: update weather data 
async def updateData(q, delay):
    while True:
        await uasyncio.sleep(delay)
        data = weather.getWeatherData()
        await q.put(data)
    
async def main():
    data = initialise()
    
    # Queue for storing weather data
    q = queue.Queue()

    pages = [pgSummary, pgTemperature, pgWind, pgRain]
    pg = 0
    
    # Run coroutines to update weather data and time
    uasyncio.create_task(updateData(q, 300))
    uasyncio.create_task(updateFooter(1))
    
    keyA_pressed = False
    keyB_pressed = False
    update = True
    tasks = []
    while True:
        if not q.empty():
            data = await q.get()
            update = True
        
        # Check for key presses
        if OLED.keyA.value() == 0:
            keyA_pressed = True    
        if OLED.keyB.value() == 0:
            keyB_pressed = True
        # Record press on key release
        if OLED.keyA.value() == 1 and keyA_pressed:
            if pg == 0:
                pg = len(pages) - 1
            else:
                pg -= 1
            keyA_pressed = False
            update = True
        if OLED.keyB.value() == 1 and keyB_pressed:
            if pg == len(pages) - 1:
                pg = 0
            else:
                pg += 1
            keyB_pressed = False
            update = True
        
        # Update page on page switch or data model change
        if update:
            for task in tasks:
                task.cancel()
            
            OLED.clearDisplay()
            tasks = pages[pg](data)
            pgNumber(pg + 1, len(pages))
            pgFooter()
            OLED.show()
            
            update = False
            
        await uasyncio.sleep(0.04)

if __name__ == '__main__':
    uasyncio.run(main())