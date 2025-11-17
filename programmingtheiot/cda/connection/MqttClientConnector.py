# programmingtheiot/cda/connection/MqttClientConnector.py

import ssl
import logging
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient

# For sensor data payload conversion if needed
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.DataUtil import DataUtil

import paho.mqtt.client as mqtt

class MqttClientConnector(IPubSubClient):
    DEFAULT_QOS = 1

    def __init__(self, client_id: str = "CDAMqttClientDefault", broker: str = "localhost", port: int = 8883, tls: bool = True):
        """
        Initialize the MQTT client connector.

        :param client_id: MQTT client ID
        :param broker: Broker hostname
        :param port: Broker port
        :param tls: Use TLS if True
        """
        self.clientID = client_id
        self.broker = broker
        self.port = port
        self.useTLS = tls
        self.logger = logging.getLogger(__name__)

        self.mqttClient = mqtt.Client(client_id=self.clientID)
        self.mqttClient.on_connect = self.onConnect
        self.mqttClient.on_disconnect = self.onDisconnect
        self.mqttClient.on_message = self.onMessage
        self.mqttClient.on_publish = self.onPublish

        if self.useTLS:
            # Update these paths to your local certs
            self.ca_cert = "/home/ernest/mosq_certs/ca.crt"
            self.client_cert = "/home/ernest/mosq_certs/server.crt"
            self.client_key = "/home/ernest/mosq_certs/server.key"

            self.mqttClient.tls_set(
                ca_certs=self.ca_cert,
                certfile=self.client_cert,
                keyfile=self.client_key,
                tls_version=ssl.PROTOCOL_TLS_CLIENT
            )

    # =====================================================================
    # Client connection methods
    # =====================================================================

    def connectClient(self) -> bool:
        try:
            self.mqttClient.connect(self.broker, self.port, keepalive=60)
            self.mqttClient.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def disconnectClient(self) -> bool:
        try:
            self.mqttClient.loop_stop()
            self.mqttClient.disconnect()
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {e}")
            return False

    # =====================================================================
    # Publishing
    # =====================================================================

    def publishMessage(self, resource: ResourceNameEnum, msg, qos: int = DEFAULT_QOS):
        """
        Publish a message to the given topic.

        Uses synchronous wait_for_publish() to ensure completion.
        """
        try:
            topic = resource.value
            msgInfo = self.mqttClient.publish(topic=topic, payload=msg, qos=qos)
            msgInfo.wait_for_publish()
        except Exception as e:
            self.logger.error(f"Failed to publish message to {resource}: {e}")

    # =====================================================================
    # MQTT callbacks
    # =====================================================================

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info(f"Connection established to {self.broker}:{self.port}")
        else:
            self.logger.warning(f"Connection failed with code {rc}")

    def onDisconnect(self, client, userdata, rc):
        self.logger.info(f"Disconnected from broker, rc={rc}")

    def onMessage(self, client, userdata, msg):
        # Handle incoming messages if required
        self.logger.debug(f"Received message on {msg.topic}: {msg.payload.decode()}")

    def onPublish(self, client, userdata, mid):
        # Temporarily disable logs for Lab 10
        pass
