import logging
import ssl
import paho.mqtt.client as mqttClient

from programmingtheiot.common.ConfigConst import *
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient
from programmingtheiot.common.IDataMessageListener import IDataMessageListener


class MqttClientConnector(IPubSubClient):

    def __init__(self, clientID: str = None):
        super().__init__()

        self.config = ConfigUtil()
        self.host = self.config.getProperty(MQTT_GATEWAY_SERVICE, HOST_KEY, DEFAULT_HOST)
        self.port = self.config.getInteger(MQTT_GATEWAY_SERVICE, PORT_KEY, DEFAULT_MQTT_PORT)
        self.securePort = self.config.getInteger(MQTT_GATEWAY_SERVICE, SECURE_PORT_KEY, DEFAULT_MQTT_SECURE_PORT)
        self.keepAlive = self.config.getInteger(MQTT_GATEWAY_SERVICE, KEEP_ALIVE_KEY, DEFAULT_KEEP_ALIVE)
        self.defaultQos = DEFAULT_QOS

        # TLS + Authentication settings
        self.enableEncryption = self.config.getBoolean(MQTT_GATEWAY_SERVICE, ENABLE_CRYPT_KEY)
        self.enableAuth = self.config.getBoolean(MQTT_GATEWAY_SERVICE, ENABLE_AUTH_KEY)
        self.pemFileName = self.config.getProperty(MQTT_GATEWAY_SERVICE, CERT_FILE_KEY)
        self.credFile = self.config.getProperty(MQTT_GATEWAY_SERVICE, CRED_FILE_KEY)

        # ---------------------------------------------------------------------
        # FIXED CREDENTIAL LOADING  (CORRECT WAY)
        # ---------------------------------------------------------------------
        self.username = None
        self.password = None

        if self.enableAuth and self.credFile:
            try:
                creds = self.config.getCredentials(MQTT_GATEWAY_SERVICE)
                if creds:
                    self.username = creds.get(USER_TOKEN_KEY)
                    self.password = creds.get(AUTH_TOKEN_KEY)
                    logging.info(f"Loaded MQTT credentials: user={self.username}")
                else:
                    logging.error("Credentials file exists but no valid credentials found.")
            except Exception as e:
                logging.error(f"Failed to load MQTT credentials: {e}")
        else:
            logging.info("Auth disabled or no credFile provided.")

        # ---------------------------------------------------------------------

        self.clientID = clientID if clientID else "PythonMqttClient_" + str(id(self))
        self.mqttClient = None

        self.dataMsgListener: IDataMessageListener = None

        self.dataUtil = DataUtil()
        self._logger = logging.getLogger(self.__class__.__name__)


    # -----------------------------------------------------------------------
    # CALLBACKS
    # -----------------------------------------------------------------------
    def onConnect(self, client, userdata, flags, rc):
        self._logger.info(f"[Callback] Connected to MQTT broker. RC={rc}")

        topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value
        try:
            client.subscribe(topic, self.defaultQos)
            self._logger.info(f"[Callback] Subscribed to {topic}")
        except Exception as e:
            self._logger.error(f"Failed to subscribe: {e}")

    def onDisconnect(self, client, userdata, rc):
        self._logger.info(f"[Callback] Disconnected from MQTT broker. RC={rc}")

    def onMessage(self, client, userdata, msg):
        self._logger.info(f"Message received on {msg.topic}")

        if not self.dataMsgListener:
            return

        try:
            payload_str = msg.payload.decode('utf-8') if isinstance(msg.payload, bytes) else msg.payload
            actuatorData = self.dataUtil.jsonToActuatorData(payload_str)

            # ALWAYS invoke listener
            self.dataMsgListener.handleActuatorCommandMessage(actuatorData)

        except Exception as e:
            self._logger.error(f"Failed to process message: {e}")

    def onPublish(self, client, userdata, mid):
        self._logger.info(f"Message published MID={mid}")

    def onSubscribe(self, client, userdata, mid, granted_qos):
        self._logger.info(f"Subscription acknowledged MID={mid}")


    # -----------------------------------------------------------------------
    # CONNECT / DISCONNECT
    # -----------------------------------------------------------------------
    def connectClient(self) -> bool:
        if not self.mqttClient:
            self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=True)

            self._logger.info(f"Using requested client ID: {self.clientID}")
            self._logger.info(f"\tMQTT Broker Host: {self.host}")
            self._logger.info(f"\tMQTT Broker Port: {self.port}")
            self._logger.info(f"\tMQTT Keep Alive: {self.keepAlive}")

            # TLS / AUTH ENABLED
            if self.enableEncryption:
                try:
                    self._logger.info("TLS enabled. Loading cert...")
                    self.port = self.securePort
                    self.mqttClient.tls_set(
                        ca_certs=self.pemFileName,
                        tls_version=ssl.PROTOCOL_TLSv1_2
                    )
                    self.mqttClient.tls_insecure_set(False)
                except Exception as e:
                    self._logger.error(f"TLS setup failed: {e}")

            if self.enableAuth and self.username and self.password:
                self._logger.info(f"Authentication enabled. Using username={self.username}")
                self.mqttClient.username_pw_set(self.username, self.password)

            # Assign callbacks
            self.mqttClient.on_connect = self.onConnect
            self.mqttClient.on_disconnect = self.onDisconnect
            self.mqttClient.on_message = self.onMessage
            self.mqttClient.on_publish = self.onPublish
            self.mqttClient.on_subscribe = self.onSubscribe

        # CONNECT
        try:
            self._logger.info(f"Attempting connection to {self.host}:{self.port}")
            self.mqttClient.connect(self.host, self.port, self.keepAlive)
            self.mqttClient.loop_start()
            return True
        except Exception as e:
            self._logger.error(f"Connection failed: {e}")
            return False


    def disconnectClient(self) -> bool:
        try:
            if self.mqttClient:
                self._logger.info("Disconnecting client...")
                self.mqttClient.loop_stop()
                self.mqttClient.disconnect()
            return True
        except Exception:
            return False


    # -----------------------------------------------------------------------
    # SUBSCRIBE / UNSUBSCRIBE / PUBLISH
    # -----------------------------------------------------------------------
    def subscribeToTopic(self, resource: ResourceNameEnum = None, callback=None, qos: int = DEFAULT_QOS) -> bool:
        if self.mqttClient and resource:
            topic = resource.value
            try:
                self.mqttClient.subscribe(topic, qos)
                if callback:
                    self.mqttClient.message_callback_add(topic, callback)
                self._logger.info(f"Subscribed to Topic={topic}, QoS={qos}")
                return True
            except Exception as e:
                self._logger.error(f"Subscribe failed: {e}")
        return False

    def unsubscribeFromTopic(self, resource: ResourceNameEnum = None) -> bool:
        if self.mqttClient and resource:
            try:
                self.mqttClient.unsubscribe(resource.value)
                return True
            except Exception:
                return False
        return False

    def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = DEFAULT_QOS) -> bool:
        if self.mqttClient and resource and msg:
            try:
                payload = msg.encode('utf-8')
                self.mqttClient.publish(resource.value, payload, qos)
                self._logger.info(f"Publishing → Topic={resource.value}")
                return True
            except Exception as e:
                self._logger.error(f"Publish failed: {e}")
        return False


    # -----------------------------------------------------------------------
    # DATA MESSAGE LISTENER
    # -----------------------------------------------------------------------
    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        if listener:
            self.dataMsgListener = listener
            return True
        return False
