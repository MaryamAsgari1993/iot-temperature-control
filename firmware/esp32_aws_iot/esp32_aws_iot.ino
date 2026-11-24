/*
 * Temperature Monitoring and Control System
 * ESP32-WROOM firmware, Concordia, Fall 2022.
 *
 * Adjusted from Appendix 1 so the program matches the system that was built:
 * a DHT11 reading goes out every 10 seconds, and AWS IoT Events decides when
 * the fan and the heater LED change. The device does not run that state
 * machine itself.
 *
 * Fill in the Wi-Fi name, the Wi-Fi password, the AWS IoT endpoint, and the
 * three PEM strings before flashing. Those values were not in the report.
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

#define DHT_SENSOR_PIN 13
#define DHT_SENSOR_TYPE DHT11
#define FAN_PIN 17
#define HEATER_PIN 23

const char* ssid = "";
const char* password = "";
const char* awsEndpoint = "";
const char* mqttClientId = "esp32_609F1C";

const char* certificate_pem_crt = "";
const char* private_pem_key = "";
const char* rootCA = "";

const char* topicOut = "outTopic";
const char* topicIn = "inTopic";
const char* topicManual = "mTopic";
const char* topicSet = "setTopic";

const unsigned long publishIntervalMs = 10000;

DHT dht(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);
WiFiClientSecure wiFiClient;
PubSubClient pubSubClient(wiFiClient);

int fanState = 0;
int heaterState = 0;
int flag2 = 0;
int automatic = 0;
float setpoint = 0;
unsigned long lastPublish = 0;
unsigned long lastMqttAttempt = 0;
bool configWarned = false;

void applyCommand(char code, bool manual);
char commandFromPayload(byte* payload, unsigned int length);
float setpointFromPayload(byte* payload, unsigned int length);
void msgReceived(char* topic, byte* payload, unsigned int length);
bool connectMqtt();

void setup() {
  Serial.begin(115200);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_PIN, OUTPUT);
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(HEATER_PIN, LOW);

  dht.begin();
  pubSubClient.setCallback(msgReceived);
  pubSubClient.setBufferSize(512);

  Serial.println("ESP32 temperature monitor");
  Serial.println("Fan on pin 17, heater LED on pin 23, DHT11 on pin 13");
}

void loop() {
  connectMqtt();
  if (millis() - lastPublish < publishIntervalMs) {
    return;
  }
  lastPublish = millis();

  float tempC = dht.readTemperature();
  if (isnan(tempC)) {
    Serial.println("DHT11 read failed");
    return;
  }
  if (!pubSubClient.connected()) {
    Serial.print("Not connected. Temperature ");
    Serial.println(tempC, 1);
    return;
  }

  char msg[160];
  snprintf(msg, sizeof(msg),
           "{\"Device_ID\":\"esp32_609F1C\",\"Fan\":%d,\"Heater\":%d,\"Flag1\":%d,\"Flag2\":%d,\"Temp\":%.1f}",
           fanState, heaterState, automatic, flag2, tempC);
  bool sent = pubSubClient.publish(topicOut, msg);
  Serial.print(sent ? "Published " : "Publish failed ");
  Serial.println(msg);
}

/*
 * inTopic and mTopic carry a fan or heater command.
 * 0 fan off, 1 fan on, 2 heater off, 3 heater on.
 * A bare character is accepted, and so is {"message":"1"} or {"message":1}.
 * mTopic is the manual dashboard, so it clears automatic mode.
 * inTopic is the AWS detector, so it marks the device automatic.
 * setTopic carries the setpoint as text, for example 23.4, or as
 * {"setpoint":23.4}. IoT Events uses that value. The ESP32 only stores it.
 */
void msgReceived(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on ");
  Serial.print(topic);
  Serial.print(": ");
  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if (strcmp(topic, topicIn) == 0) {
    applyCommand(commandFromPayload(payload, length), false);
  } else if (strcmp(topic, topicManual) == 0) {
    applyCommand(commandFromPayload(payload, length), true);
  } else if (strcmp(topic, topicSet) == 0) {
    setpoint = setpointFromPayload(payload, length);
    automatic = 1;
    flag2 = 0;
    Serial.print("The value of the setpoint is ");
    Serial.println(setpoint, 1);
  }
}

void applyCommand(char code, bool manual) {
  if (code == 0) {
    Serial.println("Command was not 0, 1, 2, or 3");
    return;
  }
  if (manual) {
    automatic = 0;
  } else {
    automatic = 1;
  }

  switch (code) {
    case '1':
      digitalWrite(FAN_PIN, HIGH);
      fanState = 1;
      Serial.println("The switch of Fan becomes ON");
      break;
    case '0':
      digitalWrite(FAN_PIN, LOW);
      fanState = 0;
      Serial.println("The switch of Fan becomes OFF");
      break;
    case '3':
      digitalWrite(HEATER_PIN, HIGH);
      heaterState = 1;
      Serial.println("The switch of Heater becomes ON");
      break;
    case '2':
      digitalWrite(HEATER_PIN, LOW);
      heaterState = 0;
      Serial.println("The switch of Heater becomes OFF");
      break;
    default:
      Serial.println("Command was not 0, 1, 2, or 3");
      break;
  }
}

char commandFromPayload(byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  if (deserializeJson(doc, (const char*)payload, length) == DeserializationError::Ok &&
      doc.containsKey("message")) {
    if (doc["message"].is<const char*>()) {
      const char* text = doc["message"];
      if (text != nullptr && text[0] != '\0') {
        return text[0];
      }
    } else {
      int value = doc["message"].as<int>();
      if (value >= 0 && value <= 3) {
        return (char)('0' + value);
      }
    }
  }
  if (length > 0 && payload[0] >= '0' && payload[0] <= '3') {
    return (char)payload[0];
  }
  return 0;
}

float setpointFromPayload(byte* payload, unsigned int length) {
  StaticJsonDocument<200> doc;
  if (deserializeJson(doc, (const char*)payload, length) == DeserializationError::Ok) {
    if (doc.containsKey("setpoint")) {
      return doc["setpoint"].as<float>();
    }
    if (doc.containsKey("message")) {
      return doc["message"].as<float>();
    }
  }
  char text[32];
  unsigned int n = length < sizeof(text) - 1 ? length : sizeof(text) - 1;
  memcpy(text, payload, n);
  text[n] = '\0';
  return atof(text);
}

bool connectMqtt() {
  if (ssid[0] == '\0' || awsEndpoint[0] == '\0' ||
      certificate_pem_crt[0] == '\0' || private_pem_key[0] == '\0' || rootCA[0] == '\0') {
    if (!configWarned) {
      Serial.println("Set ssid, password, awsEndpoint, and the three PEM strings, then flash again.");
      configWarned = true;
    }
    return false;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to Wi-Fi ");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    unsigned long started = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - started < 10000) {
      delay(250);
      Serial.print(".");
    }
    Serial.println();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wi-Fi not connected");
      return false;
    }
    Serial.print("Wi-Fi connected, IP ");
    Serial.println(WiFi.localIP());
    wiFiClient.setCACert(rootCA);
    wiFiClient.setCertificate(certificate_pem_crt);
    wiFiClient.setPrivateKey(private_pem_key);
  }

  if (!pubSubClient.connected()) {
    if (lastMqttAttempt != 0 && millis() - lastMqttAttempt < 5000) {
      return false;
    }
    lastMqttAttempt = millis();
    pubSubClient.setServer(awsEndpoint, 8883);
    Serial.print("Connecting to AWS IoT ");
    if (pubSubClient.connect(mqttClientId)) {
      pubSubClient.subscribe(topicIn);
      pubSubClient.subscribe(topicManual);
      pubSubClient.subscribe(topicSet);
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.println(pubSubClient.state());
      return false;
    }
  }

  pubSubClient.loop();
  return true;
}
