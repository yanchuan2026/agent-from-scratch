import json

import pytest

from agent.cli import main
from agent.text_stats import (
    InputDirError,
    collect_summary,
    count_chars,
    count_lines,
    count_words,
)


# ==================== 1. 正常情况 ====================
def test_count_lines_normal() -> None:
    assert count_lines("a\nb\nc") == 3


def test_count_words_normal() -> None:
    assert count_words("hello world again") == 3


def test_collect_summary_counts_all(tmp_path) -> None:
    (tmp_path / "a.txt").write_text(
        "hello world\nthis is line two\n", encoding="utf-8"
    )
    (tmp_path / "b.txt").write_text("one two three\n", encoding="utf-8")

    summary = collect_summary(tmp_path, "*.txt")

    assert summary.file_count == 2
    assert summary.total_lines == 3
    assert summary.total_words == 9


# ==================== 2. 边界情况 ====================
def test_empty_text() -> None:
    assert count_lines("") == 0
    assert count_words("") == 0
    assert count_chars("") == 0


def test_trailing_newline_does_not_add_a_line() -> None:
    assert count_lines("a\nb") == 2
    assert count_lines("a\nb\n") == 2


def test_blank_line_counts_as_a_line() -> None:
    assert count_lines("a\n\nb") == 3


def test_no_matching_files(tmp_path) -> None:
    summary = collect_summary(tmp_path, "*.txt")
    assert summary.file_count == 0
    assert summary.total_lines == 0
    assert summary.files == []


def test_pattern_filters_files(tmp_path) -> None:
    (tmp_path / "keep.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / "skip.md").write_text("b\nc\n", encoding="utf-8")

    summary = collect_summary(tmp_path, "*.txt")

    assert summary.file_count == 1


# ==================== 3. 异常情况 ====================
def test_missing_input_dir_raises(tmp_path) -> None:
    with pytest.raises(InputDirError):
        collect_summary(tmp_path / "not_here", "*.txt")


def test_non_utf8_file_raises(tmp_path) -> None:
    (tmp_path / "gbk.txt").write_bytes("中文".encode("gbk"))
    with pytest.raises(UnicodeDecodeError):
        collect_summary(tmp_path, "*.txt")


# ==================== 4. 命令行端到端 ====================
def test_cli_writes_json(tmp_path) -> None:
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "a.txt").write_text("hello\nworld\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    exit_code = main(
        ["--input", str(in_dir), "--output", str(out_dir), "--pattern", "*.txt"]
    )

    assert exit_code == 0
    data = json.loads(
        (out_dir / "summary.json").read_text(encoding="utf-8")
    )
    assert data["file_count"] == 1
    assert data["total_words"] == 2


def test_cli_missing_input_returns_2(tmp_path) -> None:
    exit_code = main(
        ["--input", str(tmp_path / "nope"), "--output", str(tmp_path / "out")]
    )
    assert exit_code == 2