# agent-stats

批量统计文本文件的行数、词数、字符数，并输出 JSON 汇总的命令行工具。

## 安装

需要 Python 3.13+ 和 uv (https://docs.astral.sh/uv/)。

    uv sync

## 用法

    uv run python -m agent.cli --input <目录> --output <目录> --pattern "<通配符>"

   参数         必填    默认值    说明
  ━━━━━━━━━━━  ━━━━━━  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   --input      是      —         要扫描的目录
  ───────────  ──────  ────────  ───────────────────────────────────────────
   --output     是      —         JSON 汇总写到哪个目录（不存在会自动创建）
  ───────────  ──────  ────────  ───────────────────────────────────────────
   --pattern    否      *.txt     文件名通配符

## 示例

sample/ 目录下有 a.txt（2 行）和 b.txt（1 行）：

    uv run python -m agent.cli --input sample --output out --pattern "*.txt"

输出：

    扫描目录  : sample
    匹配模式  : *.txt
    文件数量  : 2
    总行数    : 3
    总词数    : 9
    总字符数  : 43
    汇总已写入: out\summary.json

out/summary.json：

    {
      "input_dir": "sample",
      "pattern": "*.txt",
      "file_count": 2,
      "total_lines": 3,
      "total_words": 9,
      "total_chars": 43,
      "files": [
        { "path": "sample\\a.txt", "lines": 2, "words": 6, "chars": 30 },
        { "path": "sample\\b.txt", "lines": 1, "words": 3, "chars": 13 }
      ]
    }

## 字段说明

   字段     含义
  ━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   lines    行数，用 str.splitlines() 切分，末尾换行不额外算一行
  ───────  ──────────────────────────────────────────────────────
   words    词数，按空白字符切分
  ───────  ──────────────────────────────────────────────────────
   chars    字符数，包含空格与换行

## 运行测试

    uv run python -m pytest

## 项目结构

    src/agent/
      models.py        # pydantic 数据模型：ToolCall / FileStat / Summary
      text_stats.py    # 核心统计逻辑（纯函数，好测）
      cli.py           # 命令行入口
    tests/
      test_models.py
      test_text_stats.py

## 已知问题

• 只支持 UTF-8 编码的文件，遇到 GBK 等其他编码会直接报错退出
• 词数按空白切分，中文文本没有空格，所以中文内容的"词数"会明显偏小（字符数看 chars）
• 空行会被算作一行

 ## 实测数据

  在 `deepseek-chat`、同一问题下的行为：

   temperature    5 次调用中不同回答数
  ━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━
   0              3
  ─────────────  ──────────────────────
   1              5

  max_tokens=10 时 finish_reason 为 length（被截断）；
  max_tokens=300 时为 stop（正常结束）。

  单次调用约消耗 56 个 token，1000 次约 0.1361 元。