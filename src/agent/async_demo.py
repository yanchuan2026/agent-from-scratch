import asyncio
import time

async def fake_io(name:str,seconds:float)->str:
    """假装做一次 I0(请求网络，读文件都长这样)"""
    await asyncio.sleep(seconds)
    return f"{name}完成"

async def run_serial()->None:
    start = time.perf_counter()
    for i in range(10):
        await fake_io(f"任务{i}",1)
    print(f"串行 for+ await :{time.perf_counter() - start:.2f}秒")

async def run_concurrent()->None:
    start = time.perf_counter()
    results = await asyncio.gather(*[fake_io(f"任务{i}",1) for i in range(10)])
    print(f"gather 并发     :{time.perf_counter()-start:2f}秒" )
    print(f"gater 的返回值   :{results[0]}/共{len(results)}个")

async def main()->None:
    print("10个任务,每个耗时1秒:")
    await run_serial()
    await run_concurrent()

if __name__=="__main__":
    asyncio.run(main())

