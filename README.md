<h1>用于对实验室的示波器和信号发生器进行控制</h1> 
<h2>示波器型号：DSO-X 3104A </h2> 
<h3>目前包含函数操作</h3>  
<h5> 初始化：</h5> 
<ul>
  <li>
    <code>initialize(self,rst=1)-> None:</code>
  </li>
</ul>

<h5> 自动采集：</h5>
<ul>
  <li>
    <code>auto_capture(self):</code>
  </li>
</ul>

<h5>按设置文件设置：</h5>
<ul>
  <li>
    <code>set_by_file(self,file):</code>
  </li>
</ul>
  
<h5>设置相关：</h5> 
<ul>
<li><code>trigger_edge_set(self, **sets)-> None:</code>设置edge模式的相关参数</li> 
<li><code>scale_set()-> None：</code>采集时间基数和通道基数的设定</li>
<li><code>segm_dig()-> None:</code>分段式存储的采用和设置</li>
<li><code>rtime_dig()-> None:</code>实时采集</li>
<li><code>waveform_trans():</code>波形数据传递</li>
</ul>

<h5>保存相关：</h5>  
<ul>
<li><code>screen_save</code></li> 
<li><code>setup_save</code></li>
<li><code>waveform_save</code></li>  
</ul>

<h5>设备错误检测：</h5> 
<ul>
  <li><code>check_instrument_errors</code></li>
</ul>
