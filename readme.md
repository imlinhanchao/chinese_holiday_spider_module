# 国家节假日解析爬虫
可用于解析获取国家节假日公布页面的节假日安排。

## 使用示例
```python
from holiday import get_holiday
from datetime import datetime

# 得到当前年节假日
current_year_holiday = get_holiday(datetime.now().year)

```

## 注意
建议作为每年执行的脚本调用，而非实时API。