from typing import Any
from pydantic import BaseModel,Field,ValidationError

class ToolCall(BaseModel):
    """模型提出的一次工具调用请求"""
    name :str=Field(min_length=1,description="工具名，例如:add_task")
    """如果没有默认值的话，在初始化的时候必填"""
    arguments:dict[str,Any]=Field(default_factory=dict)#每次调用的时候生成一个新的字典，避免数据被其他实例化对象污染


class FileStat(BaseModel):
    """单个文件的统计结果"""
    path :str
    lines:int = Field(ge=0,description="行数")
    words:int = Field(ge=0,description="按空白切分的词数")
    chars:int = Field(ge=0,description="字符数，包含空格与换行")

class Summary(BaseModel):
    """一次性批量处理的汇总结果,也是最终写进json的东西"""
    input_dir:str
    pattern:str
    file_count :int=Field(ge=0)
    total_lines:int=Field(ge=0)
    total_words:int=Field(ge=0)
    total_chars:int=Field(ge=0)
    files:list[FileStat]

def main()->None:
    #实验1 正常数据
    call=ToolCall(name="add_tasks",arguments={"title":"复习 pydantic"})
    print("实验1 正常数据")
    print(" call          =",call)
    print(" call.name     =",call.name)
    print(" call.arguments=",call.arguments)
    print(" model_dump()  =",call.model_dump())
    print()

    #实验2 类型不对
    print("实验2 类型不对")
    try:
        ToolCall(name="add_task",arguments="不是字典")
    except ValidationError as exc:
        print(exc)
    print()

    #实验3 缺字段
    print("实验3 缺字段")
    try:
        ToolCall(arguments={})
    except ValidationError as exc:
        print(exc)

if __name__=="__main__":
    main()
