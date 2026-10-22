import argparse
import sys
from pathlib import Path
from agent.models import Summary
from agent.text_stats import InputDirError,collect_summary

def build_parser()->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
    prog="agent-stats",
    description="批量统计文本文件的行数，词数，字符数，并输出json汇总",
    )
    parser.add_argument("--input",required=True,type=Path,help="要扫描的目录")
    parser.add_argument("--output",required=True,type=Path,help="Json汇总写到哪个目录")
    parser.add_argument("--pattern",default="*.txt",help="文件名通配符，默认*.txt")
    return parser

def run(input_dir:Path,output_dir:Path,pattern:str)->tuple[Summary,Path]:
    summary=collect_summary(input_dir,pattern)
    output_dir.mkdir(parents=True,exist_ok=True)#f上级目录不存在就新建
    out_file= output_dir/"summary.json"
    out_file.write_text(summary.model_dump_json(indent=2),encoding="utf-8")
    return summary,out_file


def main(argv:list[str]|None=None)->int:
    args= build_parser().parse_args(argv)

    try:
        summary,out_file=run(args.input,args.output,args.pattern)
    except InputDirError as exc:
        print(f"错误：{exc}",file=sys.stderr)
        return 2
    print(f"扫描目录  : {summary.input_dir}")
    print(f"匹配模式  : {summary.pattern}")
    print(f"文件数量  : {summary.file_count}")
    print(f"总行数    : {summary.total_lines}")
    print(f"总词数    : {summary.total_words}")
    print(f"总字符数  : {summary.total_chars}")
    print(f"汇总已写入: {out_file}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
