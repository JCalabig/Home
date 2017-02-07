import socket
import I2C_LCD.I2C_LCD_driver as lcd_driver

display = lcd_driver.lcd()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 53))
ip = s.getsockname()[0]
display.lcd_display_string("IpAddr:", 1)
display.lcd_display_string(ip, 2)
