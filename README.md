# 面向事实修订的高校应急工作流一致性测试

用一个只更正地点的虚构案例检查 PATCH 响应和随后 GET 读回，再从分组记录复算论文表 3、在有限模型中重新枚举表 5。

## 运行

需要 Git、Python 3.8 或以上版本、Node.js 18 或以上版本。克隆后无需联网或安装第三方包。在空的工作目录运行（如 Python 命令名为 `python3`，请用它替换 `python`）：

```sh
git clone --depth 1 --branch v1.0.0 https://github.com/Radical0007/fact-revision-workflow-testing.git && python fact-revision-workflow-testing/reproduce.py
```

已下载仓库时，在仓库根目录运行 `python reproduce.py`。三项检查均通过时，最后一行是 `All three checks passed.`。也可单独运行以下命令。

| 命令 | 输入 | 预期结果 |
| --- | --- | --- |
| `node scripts/replay.mjs` | 虚构前态、提交体、PATCH 与 GET 观察值 | 唯一提交的事实键为 `location`。两次观察各通过 11/11 项字段检查 |
| `node scripts/table3.mjs` | 240 行按版本、请求形状、种子和模板配置导出的计数 | 修复前随机子集为 2,945/3,360 加 211/240，合计 3,156/3,600（87.67%）；修复后为 0/3,600 |
| `python scripts/table5.py` | 冻结的七种操作、长度界限 0 至 4、历史汇总五行 | 枚举 2,801 条序列，完整依赖层中原事实修订戳与文档摘要检查器误放 110 条，加入文档修订戳后为 0 条 |

## 如何核对

- **局部更新。** 打开 [单字段案例](examples/one-field.json)。对每个事实字段，提交体有该键时取提交值（字符串按契约去除首尾空白），其余取前态。程序将每个期望值分别与两个独立保存的响应比对。可以把示例另存一份，只改 GET 响应，再把副本路径传给回放程序观察哪项检查失败。离线回放运行原独立预言机中的字段检查；后端及其持久化行为只在原实验中执行。[回放方法和字段口径](docs/table3.md)
- **表 3。** 公开计数从正式实验的逐试验记录导出，每次试验最多计一次违反。脚本复算三种请求形状、两个版本及两种模板配置。B13 是实验前已知的正控。读者可以核对分组统计；逐请求报文与校内应用源码不在本仓库中。[计数来源与导出规则](docs/table3.md)
- **表 5。** 枚举程序对每条操作序列分别构造观察状态、计算历史敏感真值，并对五个检查器计数。实验在识别出文档内容恢复的例子后进行。适用范围由冻结协议的操作集、长度和依赖声明决定。[枚举方法与历史汇总](docs/table5.md)
- **第三方数据。** 论文契约实验用到 BPI Challenge 2020 Travel Permit Data。本仓库提供原 DOI、文件校验值、事件映射、案例划分与审批锚点选择步骤。[获取和预处理说明](docs/travel-permit-data.md)

## 来源与许可

| 范围 | 来源 | 许可 |
| --- | --- | --- |
| `reproduce.py`、`scripts/` | 本研究的独立测试预言机节选、有界枚举与参考检查器，以及本版回放和汇总脚本 | [MIT](LICENSE) |
| `examples/` | 为解释局部更新构造的虚构记录 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `results/`、`protocols/` | 本研究两次实验的分组计数、汇总与冻结枚举协议 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| README、`docs/` | 本研究的运行与来源说明 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 第三方旅行许可日志 | B. F. van Dongen，4TU.Centre for Research Data，2020；通过原 DOI 获取 | [原数据许可 CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) |

引用本仓库的示例、协议或记录时，请标注《面向事实修订的高校应急工作流一致性测试》复现材料、版本 v1.0.0 和仓库链接，并注明所做修改。
