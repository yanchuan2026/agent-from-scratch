# import time
# import asyncio


# async def task1():
#     print("task1开始")
#     await asyncio.sleep(5)
#     print("task2结束")
#     return 10


# async def task2():
#     print("task2开始")
#     await asyncio.sleep(2)
#     print("task2结束")
#     return 20

# async def main():
#     print("main开始")
#     result=await asyncio.gather(task1(),task2())
#     print(result)
#     print("main结束")


# if __name__=="__main__":
#     start=time.time()
#     asyncio.run(main())
#     print("总耗时:",time.time()-start)


"""关于async"""
# import time
# import asyncio

# async def task():
#     print("task完成")

# def demo():
#     temp=task()
#     asyncio.run(temp)

# if __name__=="__main__":
#     demo()


"""关于future"""
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

def thread_task(future):
    time.sleep(1)
    future.set_result(100)#表明future已经有结果了，可以返回了


async def sub_task():
    print("sub_task任务开始")
    #创建future对象
    event_loop = asyncio.get_event_loop()
    future= event_loop.create_future()
    #创建线程池对象(通过共享future对象来确定future是否完成)
    executor = ThreadPoolExecutor()
    #在其他线程执行future任务
    event_loop.run_in_executor(executor,thread_task,future)
    result = await future
    print("sub_task任务结束")
    return result

async def task1():
    print("任务1开始")
    result=await sub_task()
    print("任务1结束")
    return result

async def task2():
    print("任务2开始")
    await asyncio.sleep(10)
    print("任务2结束")
    return 200

async def main():
    result=await asyncio.gather(task1(),task2())
    print(result)
if __name__=="__main__":
    asyncio.run(main())
