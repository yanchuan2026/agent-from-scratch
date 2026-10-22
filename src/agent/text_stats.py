from pathlib import Path                                                                                                                                                                                                   
from agent.models import FileStat, Summary                                                                            
                                                                                                                        
                                                                                                                        
class InputDirError(Exception):                                                                                       
    """输入目录无效时抛出。"""                                                                                        
                                                                                                                        
                                                                                                                        
def count_lines(text: str) -> int:                                                                                    
    """行数：按换行切分后有几段。末尾有没有换行不影响结果。"""                                                        
    return len(text.splitlines())                                                                                     
                                                                                                                        
                                                                                                                        
def count_words(text: str) -> int:                                                                                    
    """词数：按空白（空格、换行、制表符）切分后有几段。"""                                                            
    return len(text.split())
                                                                                                                        
                                                                                                                        
def count_chars(text: str) -> int:
    """字符数：包含空格和换行在内的全部字符。"""                                                                      
    return len(text)                                                                                                  
                                                                                                                        
                                                                                                                        
def summarize_file(path: Path) -> FileStat:                                                                           
    """读一个文件并统计。文件不是 UTF-8 时会抛 UnicodeDecodeError。"""                                                
    text=path.read_text(encoding="utf-8")
    return FileStat(
        path=str(path),
        lines=count_lines(text),
        words=count_words(text),
        chars=count_chars(text),
    )                                                                                                 
                                                                                                                        
                                                                                                                        
def collect_summary(input_dir: Path, pattern: str = "*.txt") -> Summary:                                              
    """扫描目录里所有匹配 pattern 的文件，汇总成 Summary。"""
    if not input_dir.is_dir():
        raise InputDirError(f"输入目录错误或者不存在:{input_dir}")
    stats=[
        summarize_file(p) for p in sorted(input_dir.glob(pattern)) if p.is_file()
    ]
    return Summary(
        input_dir=str(input_dir),
        pattern=pattern,
        file_count=len(stats),
        total_lines=sum(s.lines for s in stats),
        total_words=sum(s.words for s in stats),
        total_chars=sum(s.chars for s in stats),
        files = stats,# """优先输出整体的内容,在依次输出单个文件"""
    )

                                                            