import asyncio
import logging

import aio_pika
import json
from loguru import logger as loguru_logger
from stackprinter import format as sp_format


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = loguru_logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = loguru_logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


class LowerThanWarnFormat:
    def __init__(self):
        self.format_string = "{message}"

    def __call__(self, record):
        if record["level"].no < loguru_logger.level("WARNING").no:
            return self.format_string
        else:
            return None


class WarnToExceptionFormat:
    def __init__(self):
        self.format_string = "⚠ {message}"

    def __call__(self, record):
        if loguru_logger.level("WARNING").no <= record["level"].no < loguru_logger.level("ERROR").no:
            return self.format_string
        else:
            return None


class ExceptionAndAboveFormat:
    def __init__(self):
        self.format_string = "❌ {message}"

    def __call__(self, record):
        if record["level"].no >= loguru_logger.level("ERROR").no:
            if record['exception'] is not None:
                record['extra']['stack2'] = sp_format(
                    record['exception'], truncate_vals=250, source_lines=4, reverse=True)[:3000]
            return self.format_string
        else:
            return None


class RabbitMQ:
    def __init__(self, connection_string: str, exchange_name: str, exchange_type: str):
        self.connection_string = connection_string
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self._connection = None
        self._channel = None
        self._exchange = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(self.connection_string)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name,
            self.exchange_type,
            # durable=True
        )

    async def publish_message(self, message: str, routing_key: str):
        await self._exchange.publish(
            aio_pika.Message(
                message.encode('utf-8')
            ),
            routing_key=routing_key
        )

    async def close(self):
        await self._connection.close()




class CustomLogger:
    def __init__(self, rabbitMQ: RabbitMQ):
        logging.getLogger("uvicorn").handlers.clear()
        logging.getLogger("fastapi").handlers.clear()
        logging.getLogger("aio_pika").setLevel(level=logging.WARNING)
        logging.getLogger("aiormq").setLevel(level=logging.WARNING)
        self.loguru_logger = loguru_logger
        self.rabbitmq =  rabbitMQ
        loguru_logger.remove()
        loop = asyncio.get_running_loop()
        loguru_logger.add(self.log, loop=loop, serialize=True,
                          format=self._format, filter=self._format)
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        for _log in ('uvicorn', 'uvicorn.access','fastapi'):
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

    def _format(self, record):
        lower_than_warn = LowerThanWarnFormat()
        warn_to_exception = WarnToExceptionFormat()
        exception_and_above = ExceptionAndAboveFormat()
        if lower_than_warn(record):
            return lower_than_warn.format_string
        elif warn_to_exception(record):
            return warn_to_exception.format_string
        elif exception_and_above(record):
            return exception_and_above.format_string
        return None
    
    async def close(self):
        await self.loguru_logger.complete()
        await self.rabbitmq.close()


    async def log(self, serialized_message):
        serialized_message = str(serialized_message)
        try:
            dict_msg: dict = json.loads(serialized_message)
            message: str = dict_msg["text"]
            routing_key: str = dict_msg["record"]["level"]["name"]
        except Exception as e:
            print(f"Problem while parsing json log message {serialized_message[:300]} ({type(e)}): {e}")
            return
        print(message[:400].strip())
        try:
            await self.rabbitmq.publish_message(serialized_message, routing_key)
        except (aio_pika.exceptions.ChannelClosed, 
        aio_pika.exceptions.ChannelInvalidStateError) as e:
            print(f"Problem with channel while sending message '{message}' to RabbitMQ: {e}")
        except Exception as e:
            print(f"{type(e)}: {e}")