import asyncio
import random

async def sleepy_time(sleeper_id):
    t = random.random() * 10
    print(f'[{sleeper_id}] sleeping for {t} seconds')
    status_cmd = random.choice(['true', 'false'])
    proc = await asyncio.create_subprocess_shell(f'sleep {t} ; {status_cmd}')
    exit_code = await proc.wait()
    print(f'[{sleeper_id}] done sleeping')
    return exit_code == 0

async def main():
    sleepers = [ sleepy_time(i) for i in range(5) ]

    print('waiting for sleepers')
    for coro in asyncio.as_completed(sleepers):
        res = await coro
        print(f'got result {res}')
    print('done waiting')

asyncio.run(main())
