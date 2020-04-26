import asyncio
from utils import find_free_port
from flag import random_flag_bit
from aiohttp import web


class ClosingHandler:
    def __init__(self, exit_event):
        self.exit_event = exit_event

    def next_port():
        return self.next_port

    async def default(self, request):
        self.exit_event.set()
        self.next_port = find_free_port()
        data = {
            "now": request.url.port,
            "next": self.next_port,
            "flag-slice": random_flag_slice(),
        }
        return web.json_response(data)

closers = []

# single request server
async def srs(port=None):

    # create app handler and closing event
    closing_time = asyncio.Event()
    closing_task = asyncio.create_task(closing_time.wait())
    closers.append(closing_time)
    handler = ClosingHandler(closing_time)

    # add handler to new application runner
    app = web.Application()
    app.add_routes([web.get("/", handler.default)])
    runner = web.AppRunner(app)
    await runner.setup()

    # start app on a specific tcp port
    if port == None:
        port = find_free_port()
    site = web.TCPSite(runner, "0.0.0.0", port)
    print(f"{site.name} starting")
    try:
        await site.start()
    except OSError:
        print(f"port {port} already in use, trying a different one")
        await srs()

    # wait for closing event
    await closing_task
    print(f"{site.name} closing")
    await runner.cleanup()

    await srs(handler.next_port)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    for i in range(100):
        loop.create_task(srs())

    try:
        loop.run_forever()
    except:
        print("\nexiting...")
    finally:
        for c in closers:
            c.set()  # useful event to also call runner.cleanup
