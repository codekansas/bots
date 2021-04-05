#!/usr/bin/env python

import asyncio
import logging
from typing import Dict, List, Optional

from bots.config import parse_config

logger = logging.getLogger(__name__)


async def run_one(
    bot: str,
    locks: Optional[Dict[str, asyncio.Event]] = None,
) -> None:
    backends = parse_config()
    if bot not in backends:
        available = list(backends.keys())
        logger.warning("Bot not found: %s. Available: %s", bot, available)

    for depends in backends[bot].depends:
        if locks is not None and depends in locks:
            await locks[depends].wait()

    logger.info("Running %s", bot)
    await backends[bot].run()
    if locks is not None and bot in locks:
        locks[bot].set()


async def run(bots: List[str]) -> None:
    locks = {bot: asyncio.Event() for bot in bots}
    tasks = [asyncio.create_task(run_one(bot, locks)) for bot in bots]
    for task in tasks:
        await task


def run_sync(bots: List[str]) -> None:
    asyncio.run(run(bots))
