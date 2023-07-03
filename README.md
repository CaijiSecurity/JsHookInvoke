# JsHookInvoke

现在只是Demo，只是试验一下可行性
  
### 示例

启动server  

```
python hookInvokServer.py
```

![图1](img4readme/1.png)

在控制台使用 `startHookInvoke([func1, func2, ...])` 启动Agent，传入的函数数组要按对数据处理的顺序排序  

![图2](img4readme/2.png)

server看到 从server拉取待处理的数据 和 将处理后的数据推回server 效果

![图3](img4readme/3.png)