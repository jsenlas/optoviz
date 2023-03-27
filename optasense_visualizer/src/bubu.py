import asyncio
async def do_something():
   while True:
        await asyncio.wait(10)
        print("bubu")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_something())
    loop.run_forever()
