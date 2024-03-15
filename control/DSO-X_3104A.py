# =========================================================
#mark Import modules
# =========================================================
import os #文件新建保存和关闭
import datetime #加上时间戳
import pyvisa
import struct#在需要处理二进制数据的场景中，
#如读写二进制文件，网络通信等，都可能会用到struct模块
import sys

# =========================================================
#tag class definiton:InfiniiVision示波器
# =========================================================
class InfiniiVision:
    'DSO-X_3104A示波器的类'
    def __init__(self,instr_addr,input_channel,
                 dir_data_save="D:\数据\示波器波形数据"+ os.sep + datetime.today(),
                 dir_screen_save="D:\数据\示波器屏幕"+ os.sep + datetime.today(),
                 dir_setup_save="D:\数据\配置文件"+ os.sep + datetime.today()):
        '地址，信号源，保存数据、屏幕、配置文件的路径'
        self.instr_addr = instr_addr
        self.inp_chan = input_channel#注意用编程手册规范的通道写法
        self.dir_data_save = dir_data_save
        self.dir_screen_save = dir_screen_save
        self.dir_setup_save = dir_setup_save 
        self.instrument = 0 #记录我连接的设备
        
    
    #——————————————————————————————————————————————————————————
    #mark 示波器初始化
    #——————————————————————————————————————————————————————————
    def initialize(self,rst=1):
        '对示波器初始化,连接电脑与设备.打印设备信息,清除状态并加载默认设置'
        #连接设备与电脑
        rm=pyvisa.ResourceManager()
        rm.list_resources()
        self.instrument=rm.open_resource(self.instr_addr)
        #打印设备信息
        print(self.instrument.query('*IDN?'))
        #清除状态并加载默认设置
        if rst==1:
            self.instrument.write("*CLS")
            self.instrument.write('*RST')
            print('示波器清空状态并设为默认设置')

    #——————————————————————————————————————————————————————————
    #mark 示波器数据捕获，
    #——————————————————————————————————————————————————————————
    #? 但感觉捕获部分的设备设置应该独立出来，根据我测的情况做更改
    #update 那就写一个自动化捕获的函数，然后再写一系列自定义设置的函数
    def auto_capture(self):
        '自动化捕获默认通道1,用auto-scale自动设置,然后:ACQuire模式为normal, :DIGital'        
        # 用 auto-scale 自动设置示波器，设置了“边沿触发”
        print("Autoscale.")
        self.instrument.write(":AUToscale")#自动定标

        #设置:ACQuire:TYPE
        self.instrument.write(":ACQuire:TYPE NORMal")

        #通过:DIGital数字化采集数据
        self.instrument.write(f":DIGitize {self.inp_chan}")


    #mark 按配置文件配置
    def set_by_file(self,file):
        f = open(os.file.join(dir, file),"rb")
        setup_bytes = f.read()
        f.close()
        self.instrument.write_binary_values(":SYSTem:SETup", setup_bytes)
        self.instrument.write(f":DIGitize {self.inp_chan}")

    
    #update 触发有内部有外部，每个模式触发的内容不一样所以没写完整
        #done 以后需要相关的功能再写
    #mark触发设置
    def trigger_set(self,mode = "EDGE", **sets):
        '设置模式，以及模式相关参数'
        #有效的模式命名
        modes = {"EDGE","GLITch","PATTern","TV","DELay","EBURst",
                 "OR","RUNT","SHOLd","TRANsition","SBUS{1}","SBUS{2}","USB"}
        #耦合是直流交流还有"LFReject"（50khz高通），level控制触发电压电平
        EDGE = {"耦合": "DC", "level": "5E-2","拒绝":"OFF","斜率":"POSitive","触发源":"CHANnel1"}
        #一些模式涵盖之外的命令
        func = {"噪声过滤":0, "扫描模式":"AUTO"}

        #如果输入的是有效的触发模式，则执行以下
        for mode in modes:
            command = ":TRIGger"
            match mode:
                #todo 做实验看一下不同lEVel值的效果怎么样我不是很懂
                case "EDGE":#边沿模式中有四个调整项其中level、斜率示例调整了，其它可以选调
                    for key in sets.keys():
                        if key in EDGE.key():
                            EDGE[key] = sets[key]
                        #"触发源":
                            command = ":TRIGger"+":SOURce "  +EDGE["触发源"]
                            self.instrument.write(command)
                        # "level":
                            command = ":TRIGger"+":LEVel "   +EDGE["level"]
                            self.instrument.write(command)
                        #"耦合":
                            command = ":TRIGger"+":COUPling "+EDGE["耦合"]
                            self.instrument.write(command)
                        #"斜率":
                            command = ":TRIGger"+":SLOPe "   +EDGE["斜率"]
                            self.instrument.write(command)
                        # "拒绝":
                            command = ":TRIGger"+":REJect"   +EDGE["拒绝"]
                            self.instrument.write(command)               
                        else :
                            print("EDGE不支持该参数变化")

             #如果输入的**sets的key在func.keys()当中，则把sets[key]赋值给func[key]
            if mode != "EDGE":#"EDGE"有自己的高低通滤波器选项，不知道别的有没有，没看
                for key in sets.keys():
                    if key in func.keys():
                        match sets:
                            case "噪声过滤":
                                command = ":TRIGger:NREJect 1"
                                self.instrument.write(command)
        else:                   
            print("没有该触发模式")  
    

    #mark 通道、时间基础设置
    def scale_set(self,chan_scale= "0.05V",chan_offset=0,time_scale =1.5E-7 ,time_offeset = 0,**comm):
        '采集时间基数和通道基数的设定,还有增加精准游标":VERNier",反转纵向值":INVert?",设置阻抗"IMPedance"FIFty or ONEMeg功能'
        commands={":VERNier":0,":INVert":0,"IMPedance":"ONEMeg"}
        self.instrument.write(":AUToscale")

        #通道scale和offset
        self.instrument.write(f":{self.inp_chan}:SCALe {chan_scale}")
        self.instrument.write(f":{self.inp_chan}:OFFSet {chan_offset}")
        #横向（时间基）scale和offset,time_offset是指触发发生点与屏幕显示参考点之间的差异
        self.instrument.write(f":TIMebase:SCALe {time_scale}")
        self.instrument.write(f":TIMebase:POSition {time_offeset}")

        #其它想设置的功能
        for key in comm :
            if key in commands.keys():
                commands[key]=comm[key]
                match key:
                    case ":VERNier":
                        self.instrument.write(f":{self.inp_chan}:VERNier {commands[':VERNier']}")
                    case ":INVert?":
                        self.instrument.write(f":{self.inp_chan}:InVert {commands[':INVert']}")
                    case "IMPedance":
                        self.instrument.write(f":{self.inp_chan}:IMPedance {commands['IMPedance']}")
            else:
                print("没有该功能,请自行单独向设备发送命令")       


    #mark 采集并数字化
    def dig_capture(self, mode = "RTIMe",type="NORMal"):
        ':ACQuire系(有"NORM"、"AVER"、"HRES"、"PEAK"）和:DIGital'
        modes = {"RTIMe","RITM","SEGMented","SEGM"}
        types = {"NORMal","NORM", "AVERage","AVER","HRESolution","HRES"}
        if mode in modes:
            if mode in ["SEGMented","SEGM"]:
                command = ":ACQuire:MODE SEGMented"
                self.instrument.write(command)
                print("采用分段存储模式,不可使用AVERage平均模式采集")
        else:
            print("没有这种采集模式")

        if type in types:
            command = ":ACQuire:TYPE "+type
            self.instrument.write(command)
        else:
            print("没有这种采集类型")

        #Capture an acquisition using :DIGitize.
        self.instrument.write(f":DIGitize {self.inp_chan}")


    #——————————————————————————————————————————————————————————
    #示波器数据分析，
    #——————————————————————————————————————————————————————————
    #mark 传输波形数据 points_mode可以调整但功能还没写进去
    def waveform_trans(self,name,points_mode="RAW", points=1000000,format ="WORD",pre=1):
        '可以选择是否传输数据前序pre'
        today = datetime.today()
        dir = self.dir_data_save
        if not os.path.exists(dir):
            os.makedirs(dir)
        name = name + today 

        self.instrument.write(f":WAVeform:SOURce {self.inp_chan}")
        self.instrument.write(f":WAVeform:POINts:MODE {points_mode}")
        self.instrument.write(f":WAVeform:POINts:MODE {points}")
        self.instrument.write(f":WAVeform:POINts:MODE {format}")
        #传递波形前序
        wav_form_dict = {
            0 : "BYTE",
            1 : "WORD",
            4 : "ASCii",
            }
        acq_type_dict = {
            0 : "NORMal",
            1 : "PEAK",
            2 : "AVERage",
            3 : "HRESolution",
            }
        if pre :
            #解读前序，并存为txt文件
            #把前序字符串按‘,’分开分别赋值给以下变量
            preamble_string = self.instrument.write(":WAVeform:PREamble?")
            (
            wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
            x_reference, y_increment, y_origin, y_reference
            ) = preamble_string.split(",")
            #文本内容
            txt=f"Waveform format: {wav_form_dict[int(wav_form)]}"+"\n"\
                  +f"Acquire type: {acq_type_dict[int(acq_type)]}"+"\n"\
                  +f"传输点数： {wfmpts}，波形平均数{avgcnt}"+ "\n"\
                  +f"时间步增：{x_increment}，时间起始位置：{x_origin}，起始参考点：{x_reference}"+"\n"\
                  +f"纵向步增：{y_increment}，纵向起始点：{y_origin}，起始参考点：{y_reference}"
            #指定位置写入文本
            f = open(os.file.join(dir, "pre_data"+name+".txt"), "a+") #"a+"追加在文件末尾
            f.write(txt)  
            f.close()
        
        #传入波形数据 下面的应该是有的
        # x_increment = self.instrument.write(":WAVeform:XINCrement?")
        # x_origin = self.instrument.write(":WAVeform:XORigin?")
        # y_increment = self.instrument.write(":WAVeform:YINCrement?")
        # y_origin = self.instrument.write(":WAVeform:YORigin?")
        # y_reference = self.instrument.write(":WAVeform:YREFerence?")
        #获取波形数据.
        data_bytes = self.instrument.write(":WAVeform:DATA?")
        data_bytes_length = len(data_bytes)#用于计算有多少数据
        if format == "BYTE":
            block_points = data_bytes_length
        elif format == "WORD":
            block_points = data_bytes_length / 2
        
        # 把二进制数据解码成python数据类型，%dB表示整数无符号数
        if format == "BYTE":
            values = struct.unpack("%dB" % block_points, data_bytes)
        elif format == "WORD":
            values = struct.unpack("%dH" % block_points, data_bytes)

        file = open(os.file.join(dir, name+".csv"),"a+")
        for i in range(0, len(values)-1):
            time_val = x_origin + (i * x_increment)#时间值等于起始值加步进值
            #纵向步进值是传回的值与参考点之差乘以每个点的 电压啊步进值
            voltage = ((values[i] - y_reference) * y_increment) + y_origin
            file.write(f"{time_val:E}, {voltage:f}\n")#时间用科学计数法，电压用浮点数
        
        file.close()
        print(f"{format}数据已写入示波器波形数据{name}")
        
    #mark 存示波器屏幕
    def screen_save(self,name):
        today = datetime.today()
        #创建路径
        dir = self.dir_screen_save
        if not os.path.exists(dir):
            os.makedirs(dir)

        name = name + today +".png"
        #获取示波器图片的二进制值
        screen_bytes = self.instrument.query_binary_values(":DISPlay:DATA? PNG, COLor")

        file = open( os.file.join(dir, name), 'wb')#存图片要用二进制值所以"wb"
        file.write(screen_bytes)
        file.close()
        print(f"{name}示波器屏幕已保存")

    #mark 存示波器配置
    def save_setup(self,name):
        today = datetime.today()
        dir = self.dir_setup_save
        if not os.path.exists(dir):
            os.makedirs(dir)

        name = name + today
        setup_bytes = self.instrument.query_binary_values(":SYSTem:SETup?")

        f = open(os.file.join(dir, name), "wb")
        f.write(setup_bytes)
        f.close()
        print("配置文件已保存")

    #———————————————————————————————————————————————————————————
    #mark检查设备错误
    def check_instrument_errors(command):
        error_string = InfiniiVision.query(":SYSTem:ERRor?")
        if error_string: # If there is an error string value.

            if error_string.find("+0,", 0, 3) == -1: # Not "No error".

                print(f"ERROR: {error_string}, command: '{command}'")
                print("Exited because of error.")
                sys.exit(1)
            #else:  # "No error"
                
        else: # :SYSTem:ERRor? should always return string.
            print(f"ERROR: :SYSTem:ERRor? returned nothing, command: '{command}'")
            print("Exited because of error.")
            sys.exit(1)


# =========================================================
#mark Main program:
# =========================================================
DSO_addr = "USB0::0x0957::0x17A0::MY54100202::0::INSTR"
input_channel = "CHANnel1"
setup_file_name = ""
screem_file_name = ""
data_file_name = ""

DSO = InfiniiVision(DSO_addr,input_channel)
DSO.initialize()

test = 1

if test == 1 :#测试自动定标
    DSO.auto_capture()
    DSO.dig_capture()
    DSO.waveform_trans(points=10240)
elif test == 2 :#测试自定义设置 
    #DSO.trigger_set() 先不设触发，也不自动定标，看默认状态下是怎么个事
    DSO.scale_set()   
    DSO.dig_capture()
    DSO.waveform_trans(points=10240)
elif test ==3 :#用配置文件设置
    DSO.set_by_file(setup_file_name)
    DSO.waveform_trans(points=10240)

#文件保存
DSO.screen_save(screem_file_name)
DSO.save_setup(setup_file_name)
DSO.instrument.write("")
DSO.instrument.close()
print("End of program.")
sys.exit()
