#用于对实验室的示波器和信号发生器进行控制 

##示波器型号：DSO-X 3104A  
###**目前包含函数操作**
#####**初始化：**'initialize(self,rst=1)-> None:'
#####**自动采集：**'auto_capture(self):'
#####**按设置文件设置：**'set_by_file(self,file):'
#####**设置相关：**
*'trigger_edge_set(self, **sets)-> None:'设置edge模式的相关参数
*'scale_set()-> None：'采集时间基数和通道基数的设定
*'segm_dig()-> None:'分段式存储的采用和设置
*'rtime_dig()-> None:'实时采集
*'waveform_trans():'波形数据传递
#####**保存相关：**
*'screen_save'
*'setup_save'
*'waveform_save'
#####**设备错误检测：**'check_instrument_errors'