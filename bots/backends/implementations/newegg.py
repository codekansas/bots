#!/usr/bin/env python

import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import requests
from bots.backends.interfaces.cron_interface import CronBackend
from bots.backends.registry import register
from bots.utils import Time
from lxml import html

logger = logging.getLogger(__name__)


class NeweggBackend(CronBackend):
    def __init__(self, name: str, config: Dict[str, str]) -> None:
        # Parses the DB path.
        self.db: Path = Path(config["db"])
        config.pop("db")

        # Parses the table path.
        self.table: str = config["table"]
        config.pop("table")

        self._conn: Optional[sqlite3.Connection] = None
        self.connect()

        super().__init__(name, config)

    def connect(self) -> None:
        if not self.db.exists():
            self.db.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(self.db)
        cur = self.conn.cursor()

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                time text NOT NULL,
                id text NOT NULL,
                name text NOT NULL,
                in_stock integer NOT NULL,
                price float NOT NULL
            );
        """)

        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS {self.table}_index
            ON {self.table}(time, id)
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.exception_table} (
                time text NOT NULL,
                exception text NOT NULL
            )
        """)

        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS {self.exception_table}_index
            ON {self.exception_table}(time)
        """)

    @property
    def exception_table(self) -> str:
        return f"{self.table}_exceptions"

    @property
    def conn(self) -> sqlite3.Connection:
        conn = self._conn
        assert conn is not None
        return conn

    def __del__(self) -> None:
        if self._conn is not None:
            self._conn.close()

    def log_exception(self, exception: str) -> None:
        time = Time.get()
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO {self.exception_table} (?, ?)",
                    (time, exception))
        self.conn.commit()

    def props(self) -> Dict[str, Any]:
        return {**super().props(), "db": self.db, "table": self.table}


@register("newegg-availability")
class NeweggAvailabilityBackend(NeweggBackend):
    """Checks availability of products on Newegg and saves to an SQLite table.

    The product search parameters should be specified as a JSON list. They are
    joined with `%` to get the N parameter for the URL.
    """

    def __init__(self, name: str, config: Dict[str, str]) -> None:
        # Parses the product IDs.
        search = json.loads(config["search"])
        assert isinstance(search, list), search
        config.pop("search")

        self.url = f"https://newegg.com/p/pl?N={'%'.join(search)}&PageSize=96"

        super().__init__(name, config)

    async def run(self) -> None:
        time = Time.get()

        response = requests.get(self.url)
        if response.status_code != 200:
            self.log_exception(f"Got status code: {response.status_code}")
            return

        tree = html.fromstring(response.content)
        elements = tree.xpath("//div[contains(@class, 'item-container')]")

        # Gets item names.
        names = [
            [
                (p.text_content(), re.findall(r"/p/([\w\d]+)", p.get("href")))
                for p in element.xpath(".//a[contains(@class, 'item-title')]")
            ] for element in elements
        ]

        # Checks if the item is out of stock.
        out_of_stocks = [
            any(
                p.text_content() == "OUT OF STOCK"
                for p in element.xpath(".//p[contains(@class, 'item-promo')]")
            ) for element in elements
        ]

        # Checks the item price.
        prices = [
            [float(p.replace(",", "")) for p in price_list]
            for element in elements
            for price_list in [
                re.findall(r"[\d,]+\.\d+", p.text_content())
                for p in element.xpath(".//li[contains(@class, 'price-current')]")
            ]
        ]

        # Sanitizes all the gross XPath outputs.
        all_items = []
        for name, out_of_stock, price in zip(names, out_of_stocks, prices):
            if not name:
                continue
            name_str, ids = name[0]
            if not ids:
                continue
            id_str = ids[0]
            in_stock = 0 if out_of_stock else 1
            if not price:
                continue
            price_str = price[0]
            all_items += [(time, id_str, name_str, in_stock, price_str)]

        cur = self.conn.cursor()
        cur.executemany(f"INSERT INTO {self.table} VALUES (?, ?, ?, ?, ?)",
                        all_items)
        self.conn.commit()

        logger.info("Inserted %d rows", len(all_items))

    def props(self) -> Dict[str, Any]:
        return {**super().props(), "url": self.url}


@register("newegg-availability-graph")
class NeweggAvailabilityGraphBackend(NeweggBackend):
    """Creates a graph of product availability and prices.

    This simply reads from the table that is created by `newegg-availability`
    task and plots the price and availability over time.
    """

    def __init__(self, name: str, config: Dict[str, str]) -> None:
        # Parses the graph path.
        self.graph = Path(config["graph"])
        config.pop("graph")

        super().__init__(name, config)

    async def run(self) -> None:
        cur = self.conn.cursor()

        cur.execute(f"""
            SELECT time, max(in_stock), avg(price)
            FROM {self.table}
            GROUP BY time
        """)

        rows = cur.fetchall()
        time, in_stock, price = zip(*rows)
        time, in_stock, price = list(time), list(in_stock), list(price)
        time = [Time.parse(t) for t in time]

        plt.figure(figsize=(16, 8))

        plt.subplot(2, 1, 1)
        plt.plot(time, in_stock, marker="o")
        plt.title("In Stock")
        plt.gcf().autofmt_xdate()

        plt.subplot(2, 1, 2)
        plt.plot(time, price, marker="o")
        plt.title("Price")
        plt.gcf().autofmt_xdate()

        plt.savefig(self.graph)

        logger.info("Saved to %s", self.graph)
