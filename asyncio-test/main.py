import asyncio
import random

async def sleepy_time(sleeper_id):
    t = random.random() * 10
    print(f'[{sleeper_id}] sleeping for {t} seconds')
    await asyncio.sleep(t)
    print(f'[{sleeper_id}] done sleeping')

async def main():
    sleepers = [ sleepy_time(i) for i in range(5) ]

    print('waiting for sleepers')
    for sleeper in sleepers:
        await sleeper
    print('done waiting')

asyncio.run(main())
