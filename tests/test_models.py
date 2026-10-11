import pytest
from pydantic import ValidationError

from agent.models import ToolCall

#1 正常情况
def test_normal_call_keeps_values()->None:
    """合法数据应当原样保留"""
    call = ToolCall(name="add_task",arguments={"title":"复习 pydantic"})
    assert call.name=="add_task"
    assert call.arguments=={"title":"复习 pydantic"}

def test_arguments_can_be_omitted()->None:
    """arguments有默认值,可以只传name"""
    call = ToolCall(name="list_tasks")
    assert call.arguments=={}

#2,边界情况
@pytest.mark.parametrize("length",[1,2,3,20])
def test_name_of_various_lengths(length:int)->None:
    """min_len=1，长度为1就是最小合法边界"""
    call=ToolCall(name="a"*length)
    assert len(call.name)==length

@pytest.mark.parametrize(
    ("raw","expected"),
    [
        ({},{}),
        ({"status":"todo"},{"status":"todo"}),
        ({"n":1,"flag":True},{"n":1,"flag":True}),
    ],
)

def test_arguments_round_trip(raw:dict,expected:dict)->None:
    """arguments是dict[str,Any],各种键值都要能存住"""
    call=ToolCall(name="add_task",arguments=raw)
    assert call.arguments==expected

#3异常情况
def test_empty_name_raises()->None:
    with pytest.raises(ValidationError):
        ToolCall(name="")

def test_none_name_raises()->None:
    with pytest.raises(ValidationError):
        ToolCall(name=None)

def test_int_name_raises()->None:
    """pydantic不会把int转为str"""
    with pytest.raises(ValidationError):
        ToolCall(name=123)

def test_wrong_arguments_type_raises()->None:
    with pytest.raises(ValidationError):
        ToolCall(name="add_tasks",arguments="不是字典")

def test_missing_name_raises()->None:
    with pytest.raises(ValidationError):
        ToolCall(arguments={})




