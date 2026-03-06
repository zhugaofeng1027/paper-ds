# Agent-analys

这个项目现在支持两件事：

1. 根据关键词（不区分大小写）爬取多个顶会论文标题，并保存到 `txt/`。
2. 对保存的 `.txt` 标题做统计分析，输出热点子领域结论与可视化图。

## 环境安装

```bash
pip install -r requirements.txt
```

如果 `python` 不可用，可用 `py -3` 替代。

## 一键执行（推荐）

```bash
py -3 pipeline.py all -k Agent --years 2023,2024,2025 --venues acl,cvpr,iccv,eccv,neurips,icml,iclr
```

执行后会生成：

- `txt/agent_papers_<venue><year>_<count>.txt`：每个会/年份的匹配标题
- `txt/agent_all_titles.txt`：合并去重后的总标题
- `report/agent_analysis_report.md`：分析报告（词频、短语、主题分布、研究建议）
- `plot/agent_theme_distribution.png`：主题分布柱状图

## 分步执行

先爬取：

```bash
py -3 pipeline.py crawl -k Agent --years 2025 --venues acl,cvpr
```

再分析：

```bash
py -3 pipeline.py analyze -k Agent
```

## 参数说明

- `-k, --keyword`：关键词，例如 `Agent`、`Reasoning`
- `--years`：年份列表，逗号分隔，例如 `2023,2024,2025`
- `--venues`：会议列表，逗号分隔
  - 可选：`acl,cvpr,iccv,eccv,neurips,icml,iclr`
- `--txt-dir`：标题保存目录（默认 `txt`）
- `--report-dir`：报告目录（默认 `report`）
- `--plot-dir`：图表目录（默认 `plot`）
- `--from-file`：只分析某一个 txt 文件（用于 `analyze`）

