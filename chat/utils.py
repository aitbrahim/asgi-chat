import asyncio
from concurrent.futures import CancelledError


async def await_many_dispatch(consumer_callables, dispatch):
    """
    Given a set of consumer callables, awaits on them all and passes results
    from them to dispatch awaitable as they come in.
    """
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(consumer_callable())
        for consumer_callable in  consumer_callables
    ]
    try:
        while True:
            # wait for any of them to complete
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for i, task in enumerate(tasks):
                if task.done():
                    result = task.result()
                    await dispatch(result)
                    tasks[i] = asyncio.ensure_future(consumer_callables[i]())
    finally:
        # make sure we clean up tasks on exit
        for task in tasks:
            task.cancel()
            try:
                await task
            except CancelledError:
                pass
