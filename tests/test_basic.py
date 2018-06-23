#!/usr/bin/env python3
import asynctest
import logging
import asyncio

from asyncpool import AsyncPool


class WorkPoolTestCases(asynctest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.basicConfig(level=logging.INFO)
        self._logger = logging.Logger('')
        self._evt_wait = None

    async def setUp(self):
        self._evt_wait = asyncio.Event()

    async def tearDown(self):
        self._evt_wait.set() # unblock any blocked workers

    async def test_worker_limit(self):
        num_called = 0

        evt_hit = asyncio.Event()

        async def worker(param):
            nonlocal num_called
            num_called += 1
            assert param == 5
            evt_hit.set()
            await self._evt_wait.wait()

        async with AsyncPool(None, 5, '', self._logger, worker) as wq:
            # tests that worker limit/load factor of 1 works correctly
            for _ in range(10):  # five workers plus 5 in queue
                await asyncio.wait_for(wq.push(5), 1)

            self.assertEqual(num_called, 5)

            with self.assertRaises(asyncio.TimeoutError):
                # with load_factor==1, and all workers stuck we should timeout
                await asyncio.wait_for(wq.push(5), 1)

            self.assertEqual(wq.total_queued, 10)

            # unblock workers
            self._evt_wait.set()
            await asyncio.sleep(1)  # clear the workers

            evt_hit.clear()

            await asyncio.wait_for(wq.push(5), 1)
            await asyncio.wait_for(evt_hit.wait(), 1)
            self.assertEqual(num_called, 11)
            self.assertFalse(wq.exceptions)

    async def test_load_factor(self):
        async def worker(param):
            await self._evt_wait.wait()

        async with AsyncPool(None, 5, '', self._logger, worker, 2) as wq:
            for _ in range(15):  # 5 in-flight, + 10 in queue per load factor
                await asyncio.wait_for(wq.push(5), 1)

            with self.assertRaises(asyncio.TimeoutError):
                # with load_factor==1, and all workers stuck we should timeout
                await asyncio.wait_for(wq.push(5), 1)

            # unblock workers
            self._evt_wait.set()
            await asyncio.sleep(1)  # let them clear the queue

            await asyncio.wait_for(wq.push(5), 1)
            self.assertFalse(wq.exceptions)

    async def test_task_timeout(self):
        async def worker(param):
            await self._evt_wait.wait()

        async with AsyncPool(None, 5, '', self._logger, worker, max_task_time=1, return_futures=True) as wq:
            fut = await asyncio.wait_for(wq.push(5), 1)

            for i in range(5):
                await asyncio.sleep(1)

                if fut.done():
                    e = fut.exception()
                    self.assertIsInstance(e, asyncio.TimeoutError)
                    self.assertTrue(wq.exceptions)
                    return

            self.fail('future did not time out')

    async def test_join(self):
        key = 'blah'

        async def worker(param):
            await asyncio.sleep(1)  # wait a sec before returning result
            return param

        async with AsyncPool(None, 5, '', self._logger, worker, return_futures=True) as wq:
            fut = await asyncio.wait_for(wq.push('blah'), 0.1)
            self.assertFalse(fut.done())

        self.assertTrue(fut.done())
        result = fut.result()
        self.assertEqual(result, key)


if __name__ == '__main__':
    asynctest.main()
