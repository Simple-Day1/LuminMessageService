import nats
import json
from nats.js.api import ConsumerConfig, DeliverPolicy, AckPolicy
from typing import Callable, Type
from LuminMessageService.app.domain.events.domain_event import DomainEvent
from LuminMessageService.app.domain.events.event_bus import EventBus
from LuminMessageService.app.domain.models.aggregates.aggregate_root import AggregateRoot


class NatsEventBus(EventBus):
    def __init__(self, nats_url: str = "nats://localhost:4222") -> None:
        self.nats_url = nats_url
        self.nc = None
        self.js = None
        self._stream_name = "MESSAGES_EVENTS"
        self._handlers: dict[str, list[Callable]] = {}
        self.stream_subscriptions = {}

    async def connect(self):
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            await self._setup_stream()
        except Exception as e:
            print(f"Error connecting to NATS: {e}")
            raise

    async def _setup_stream(self):
        try:
            print("✅ Stream {self._stream_name} setup complete")
        except Exception as e:
            if "stream name already in use" in str(e):
                print(f"ℹ️ Stream {self._stream_name} already exists")
            else:
                print(f"Stream setup error: {e}")

    async def publish(self, event: DomainEvent) -> None:
        if not self.js:
            await self.connect()

        try:
            event_data = event.to_dict()
            subject = f"message.events.{event.event_type}"

            await self.js.publish(
                subject=subject,
                payload=json.dumps(event_data, default=str).encode()
            )
            print(f"Event published: {event.event_type}")
        except Exception as e:
            print(f"Error publishing event: {e}")
            raise

    async def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        subject = f"message.events.{event_type.__name__}"

        if subject not in self._handlers:
            self._handlers[subject] = []
        self._handlers[subject].append(handler)

        try:
            consumer_config = ConsumerConfig(
                durable_name=f"{event_type.__name__}-consumer",
                deliver_policy=DeliverPolicy.NEW,
                ack_policy=AckPolicy.EXPLICIT,
            )

            sub = await self.js.pull_subscribe(
                subject=subject,
                durable=consumer_config.durable_name
            )
            self.stream_subscriptions[subject] = sub
        except Exception as e:
            print(f"Subscription error: {e}")

    async def process_events(self, aggregate: AggregateRoot) -> None:
        for event in aggregate.get_domain_events():
            await self.publish(event)
        aggregate.clear_domain_events()
