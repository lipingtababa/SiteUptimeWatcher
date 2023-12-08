import asyncio, time


async def hello_world(msg, interval=1.0):
    while True:
        print(msg)
        await asyncio.sleep(interval)


def print_hello():
    print(type(hello_world))
    loop = asyncio.get_event_loop()
    coro1 = hello_world("Hello World")
    coro2 = hello_world("Ni hao", 2.0)
    print(type(coro1))

    task = loop.create_task(coro1)
    task = loop.create_task(coro2)

    loop.run_until_complete(task)
    loop.close()

def get_number():
    values = range(100)

    for i in values:
        if i % 2 == 0:
            yield i

def yield_test():
    nums_ = get_number()

    print(type(get_number))
    print(type(nums_))
    while True:
        x = next(nums_)
        print(x)
        if x > 10:
            break

yield_test()