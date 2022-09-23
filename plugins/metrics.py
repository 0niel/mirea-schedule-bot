from kutana import Plugin
import psutil
import time
import os


plugin = Plugin(name="Metrics", description="Send some information")


@plugin.on_commands(["metrics"])
async def _(msg, ctx):
    process = psutil.Process(os.getpid())

    taken_memory = int(process.memory_info().rss / 2**20)
    taken_time = time.time() - msg.date

    await ctx.reply(f"memory: ~{taken_memory}mib; time: {taken_time}s")