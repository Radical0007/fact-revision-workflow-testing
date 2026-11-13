# 获取和预处理旅行许可日志

B. F. van Dongen（2020），*BPI Challenge 2020: Travel Permit Data*，4TU.Centre for Research Data，第 1 版。原始日志适用 CC BY-NC 4.0。原数据和派生轨迹由读者自行获取和处理。表 3 和表 5 的复算均无需该数据集。[数据 DOI](https://doi.org/10.4121/uuid:ea03d361-a7cd-4f5e-83d8-5fbdf0362550) · [原许可](https://creativecommons.org/licenses/by-nc/4.0/)

1. 在 DOI 页面选择 **PermitLog.xes.gz**。研究使用的压缩文件 SHA-256 为 `9e23befe5394c13caff4428c00a6cee08647b1749f270a78cd05d99f861c5a8b`。在下载目录执行下列命令核对文件。

   ```sh
   python -c "import hashlib, pathlib; print(hashlib.sha256(pathlib.Path('PermitLog.xes.gz').read_bytes()).hexdigest())"
   ```

2. 解压并读取 XES。按 XML 中的顺序遍历每个 `trace`，从 1 开始分配六位本地序号，如 `case_000001`。每个案例中的事件也保持 XML 顺序，位置从 0 开始。保留事件的 `concept:name`。有 ` by ` 后缀的活动取最后一个后缀作为角色类别，其余记为 `SYSTEM_OR_UNSPECIFIED`。省略原案例标识、资源标识、时间戳、金额和组织属性。该版本应得到 7,065 个案例、86,581 个事件、51 种活动和 1,478 种活动序列。

3. 对每个案例取 `SHA256(UTF8("revision-consistency-bpi2020-v1" + case_id))`，按十六进制摘要升序排列。前 1,413 个案例进入试验组（pilot），余下 5,652 个案例留出。先按原案例划分，再派生片段，同一案例的所有派生片段归入同一组。

4. 在留出案例中寻找活动名含 ` APPROVED by ` 或 ` FINAL_APPROVED by ` 的事件作为审批锚点。47 个案例没有锚点，其余 5,605 个案例适用。原实验分别使用种子 11011、22022、33033、44044、55055。对每个案例与种子，以 `SHA256(UTF8(case_id + "|" + 十进制种子))` 的前 8 字节按大端解释为整数，初始化 Python 的 `random.Random`，用第一次 `randrange` 从按事件顺序排列的候选锚点中选择一项。

日志提供审批位置、角色和事件顺序。论文中用到的事实、依赖、文档修改和失效标签由实验构造。这里提供获取与预处理说明；本仓库的运行命令覆盖局部更新回放、表 3 和表 5。
