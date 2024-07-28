import sensor, image,time,pyb
from pyb import UART,LED
import json
import ustruct
import utime

THRESHOLD = [(0, 39, -128, 127, -128, 127)]

LED(1).on()
LED(2).on()
LED(3).on()

sensor.reset()
#sensor.set_vflip(True)
#sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA) # 80x60 (4,800 pixels) - O(N^2) max = 2,3040,000.
#sensor.set_windowing([0,20,80,40])
sensor.skip_frames(time = 2000)     # WARNING: If you use QQVGA it may take seconds
clock = time.clock()                # to process a frame sometimes.

uart = UART(3,9600)   #定义串口3变量
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters初始化串口

while(True):
    clock.tick()
    img = sensor.snapshot()
    img.erode(1)    # 腐蚀的程度或者次数
    img.binary(THRESHOLD)
    # histogram = img.get_histogram()
    # Thresholds = histogram.get_threshold()
    # img.binary([(0,Thresholds.value())])    # image.binary像素格式
    line = img.get_regression([(100,100)], robust = True)
    # robust=True 为采用theil—sen回归算法，跳过的x像素数和y像素数均为100
    if (line):    # 如果识别到路线
        rho_err = abs(line.rho())-img.width()/2
        h=rho_err
        if h<0:
            a = 0x01
            rho_err =-rho_err
        else:
            a = 0x03
        if line.theta()>90:        # 如果回归算法得到的角度大于90
            theta_err = line.theta() - 180     # 则theta等于其补角
        else:
            theta_err = line.theta()      # 否则theta等于本身
        img.draw_line(line.line(), color = 127)   # 返回一个直线元组(x1, y1, x2, y2)并用特定颜色用于划线
        #print(h)  #霍夫变换后的直线的模(magnitude)
        magnitude = line.magnitude()
        #FH = bytearray([0x2C])
        #uart.write(FH)
        if a == 0x03 :
            rho_err = -rho_err;
        Send_buf = "error->" + ("%.3d\r\n") % rho_err
        print(Send_buf)
        uart.write(Send_buf)
