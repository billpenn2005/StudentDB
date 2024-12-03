主页面：
```
设计html页面，含有基本信息窗,课表窗和登出按钮，其中基本信息窗在页面启动时向/api/basicinfo发送post获取信息，若state为Failed则显示错误，若state为Success则获取role和name并显示,若role为Student则获取student_id显示，若role为Teacher则获取teacher_id显示，登出按钮按下时向/auth/logoutapi发送post，若回复state为Success则刷新页面，否则报错，课表通过向api/courseinfo发送POST获取，json中的数组courses为课程信息，每个课程信息有'name','day','slot','teacher',其中slot为时间段，整型0到4，分别表示上午第一和二节下午一和二节和晚课，day表示周几（1-7），根据信息显示（从周一到周日为行，课程时间段（5个）为列，name和teacher为表格内容）
```