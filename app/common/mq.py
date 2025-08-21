import json
import aio_pika
from types import SimpleNamespace
from aio_pika import (
    ExchangeType,
    Message,
    DeliveryMode,
)
from . import settings
from contextlib import asynccontextmanager


async def open_mq():
    connection = await aio_pika.connect_robust(
        settings.AMQP_URL
    )
    channel = await connection.channel(
        publisher_confirms=True,
    )
    await channel.set_qos(50)
    return connection, channel

async def declare_topology(channel):
    exchange = await channel.declare_exchange(
        settings.RABBITMQ_EXCHANGE,
        ExchangeType.TOPIC,
        durable=True,
    )
    create = await channel.declare_queue(
        settings.QUEUE_TASK_CREATE,
        durable=True,
    )
    result = await channel.declare_queue(
        settings.QUEUE_TASK_RESULT,
        durable=True,
    )
    await create.bind(
        exchange,
        routing_key=settings.QUEUE_TASK_CREATE,
    )
    await result.bind(
        exchange,
        routing_key=settings.QUEUE_TASK_RESULT,
    )
    return exchange, create, result

async def pub_json(exchange, routing_key: str, payload: dict):
    body = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")
    msg = Message(
        body=body,
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await exchange.publish(
        msg,
        routing_key=routing_key,
    )
    
@asynccontextmanager
async def mq_lifespan(app):
    conn, ch = await open_mq()
    try:
        exch, create, result = await declare_topology(ch)
        app.state.mq = SimpleNamespace(
            conn=conn,
            ch=ch,
            exch=exch,
            create=create,
            result=result,
        )
        yield
    finally:
        await ch.close()
        await conn.close()