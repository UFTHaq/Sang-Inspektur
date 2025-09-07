#include <Arduino.h>
#include <WiFi.h>

#include <FastLED.h>

#define RGB_PIN 48
#define NUM_LED 1

CRGB leds[NUM_LED];

const char* ssid = "ESP32S3_AP";
const char* password = "12345678";

WiFiServer server(5001);  // ESP32 listens on port 5001

void turnOFFLED()
{
  FastLED.addLeds<WS2812B, RGB_PIN, GRB>(leds, NUM_LED);
  leds[0] = CRGB::Black;
  FastLED.show();
}

void setup() {
  Serial.begin(115200);
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(IPAddress(192,168,4,1), IPAddress(192,168,4,1), IPAddress(255,255,255,0));
  server.begin();
  Serial.println("ESP32 AP running, waiting for Pi5...");

  turnOFFLED();
}

void loop() {
//   rgbLedWrite(RGB_PIN, 0, 0, 0); // Turn OFF.

  WiFiClient client = server.available();
  if (client) {
    while (client.connected()) {
      if (client.available()) {
        String data = client.readStringUntil('\n');
        Serial.println("Received from Pi5: " + data);
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}


