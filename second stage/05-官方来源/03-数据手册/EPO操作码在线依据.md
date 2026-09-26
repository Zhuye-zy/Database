# DOCDB状态处理依据

EPO 官方 DOCDB XML Exchange Format / ST36 User Documentation，PDF第27–36页，特别是第36页CV/DV说明。

https://link.epo.org/web/T09.01%20ST36%20User%20Documentation%20vs%202.5.8.pdf

A/C按业务键更新或插入；D记录软删除；CV/DV记入撤回通知审计，不补造普通专利。DeleteRekey包应先于其他变更处理。

本轮已通过网页工具读取官方原文；WSL直接下载返回HTTP403，因此没有伪称本地已归档PDF。四类数据及法律样例的五份CNIPA手册仍完整保留。
