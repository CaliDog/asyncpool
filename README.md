# AsyncPool

Asyncio coroutine worker pool. No more juggling bounded semaphores and annoying timeouts, and allows you to run through millions of pieces of data efficiently. 

Adapted from the awesome worker pool found at https://gist.github.com/thehesiod/7081ab165b9a0d4de2e07d321cc2391d

# Example Usage

```python
import asyncpool
import logging
import asyncio

async def example_coro(initial_number, result_queue):
    print("Processing Value! -> {} * 2 = {}".format(initial_number, initial_number * 2))
    await asyncio.sleep(1)
    await result_queue.put(initial_number * 2)

async def result_reader(queue):
    while True:
        value = await queue.get()
        if value is None:
            break
        print("Got value! -> {}".format(value))

async def run():
    result_queue = asyncio.Queue()

    reader_future = asyncio.ensure_future(result_reader(result_queue), loop=loop)

    # Start a worker pool with 10 coroutines, invokes `example_coro` and waits for it to complete or 5 minutes to pass.
    async with asyncpool.AsyncPool(loop, num_workers=10, name="ExamplePool",
                             logger=logging.getLogger("ExamplePool"),
                             worker_co=example_coro, max_task_time=300,
                             log_every_n=10) as pool:
        for i in range(50):
            await pool.push(i, result_queue)

    await result_queue.put(None)
    await reader_future

loop = asyncio.get_event_loop()

loop.run_until_complete(run())

```
