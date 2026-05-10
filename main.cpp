#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>

// =======================
// CONFIGURACIÓN
// =======================
#define INTERVALO_MS 2000

// =======================
// PINES ESP32-S3
// =======================
#define PIN_I2C_SDA   8
#define PIN_I2C_SCL   9

#define PIN_SOIL1_ADC 4
#define PIN_UV_ADC    5
#define PIN_SOIL2_ADC 6

#define PIN_PUMP      12
#define PIN_LEDS      15

// =======================
// SENSOR BH1750
// =======================
BH1750 lightMeter;
bool bh1750_ok = false;

// =======================
// FUNCIONES
// =======================
float adcToVoltage(int raw) {
  return (raw * 3.3f) / 4095.0f;
}

void imprimirEncabezadoCSV() {
  Serial.println(
    "timestamp_ms,"
    "soil1_raw,soil1_v,"
    "soil2_raw,soil2_v,"
    "soil_avg_raw,"
    "uv_raw,uv_v,"
    "lux,"
    "pump_state,"
    "leds_state"
  );
}

void setup() {
  Serial.begin(115200);
  delay(3000);

  analogReadResolution(12);
  analogSetPinAttenuation(PIN_SOIL1_ADC, ADC_11db);
  analogSetPinAttenuation(PIN_SOIL2_ADC, ADC_11db);
  analogSetPinAttenuation(PIN_UV_ADC, ADC_11db);

  pinMode(PIN_PUMP, OUTPUT);
  pinMode(PIN_LEDS, OUTPUT);

  digitalWrite(PIN_PUMP, LOW);
  digitalWrite(PIN_LEDS, LOW);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(100000);
  delay(500);

  bh1750_ok = lightMeter.begin(
    BH1750::CONTINUOUS_HIGH_RES_MODE,
    0x23,
    &Wire
  );

  Serial.println("# MACETA INTELIGENTE");
  Serial.println("# MODO CSV ACTIVO");
  Serial.print("# BH1750=");
  Serial.println(bh1750_ok ? "OK" : "NO_DETECTADO");

  imprimirEncabezadoCSV();
}

void loop() {
  unsigned long timestamp = millis();

  int soil1Raw = analogRead(PIN_SOIL1_ADC);
  int soil2Raw = analogRead(PIN_SOIL2_ADC);
  int uvRaw = analogRead(PIN_UV_ADC);

  float soil1V = adcToVoltage(soil1Raw);
  float soil2V = adcToVoltage(soil2Raw);
  float uvV = adcToVoltage(uvRaw);

  int soilAvgRaw = (soil1Raw + soil2Raw) / 2;

  float lux = -1.0;

  if (bh1750_ok) {
    lux = lightMeter.readLightLevel();
  }

  int pumpState = digitalRead(PIN_PUMP);
  int ledsState = digitalRead(PIN_LEDS);

  Serial.print(timestamp);
  Serial.print(",");

  Serial.print(soil1Raw);
  Serial.print(",");
  Serial.print(soil1V, 3);
  Serial.print(",");

  Serial.print(soil2Raw);
  Serial.print(",");
  Serial.print(soil2V, 3);
  Serial.print(",");

  Serial.print(soilAvgRaw);
  Serial.print(",");

  Serial.print(uvRaw);
  Serial.print(",");
  Serial.print(uvV, 3);
  Serial.print(",");

  Serial.print(lux, 2);
  Serial.print(",");

  Serial.print(pumpState);
  Serial.print(",");

  Serial.println(ledsState);

  delay(INTERVALO_MS);
}