import serial
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
import sys

# =======================
# CONFIGURACIÓN
# =======================
PUERTO = "COM4"       # Cambia si tu ESP32 usa otro COM
BAUDIOS = 115200
MAX_MUESTRAS = 100
ARCHIVO_CSV = "datos_maceta.csv"

# =======================
# ABRIR SERIAL
# =======================
try:
    ser = serial.Serial()
    ser.port = PUERTO
    ser.baudrate = BAUDIOS
    ser.timeout = 2

    # No reiniciar automáticamente la ESP32
    ser.dtr = False
    ser.rts = False

    ser.open()
    time.sleep(2)

except Exception as e:
    print("ERROR ABRIENDO PUERTO SERIAL")
    print(e)
    print("\nRevisa:")
    print("- Que el puerto COM sea correcto.")
    print("- Que no esté abierto PlatformIO Monitor.")
    print("- Que el ESP32 esté conectado.")
    sys.exit()

# =======================
# VARIABLES
# =======================
lineas = []
header = None

print("\n======================================")
print(" LECTURA DE SENSORES - MACETA")
print("======================================")
print(f"Puerto: {PUERTO}")
print(f"Baudios: {BAUDIOS}")
print(f"Muestras objetivo: {MAX_MUESTRAS}")
print("--------------------------------------")
print("Si no aparecen datos, presiona RESET/EN manualmente.")
print("======================================\n")

# =======================
# LECTURA SERIAL
# =======================
try:
    while len(lineas) < MAX_MUESTRAS:
        try:
            linea = ser.readline().decode(errors="ignore").strip()
        except serial.SerialException as e:
            print("\nERROR SERIAL DURANTE LECTURA")
            print(e)
            ser.close()
            sys.exit()

        if not linea:
            continue

        if linea.startswith("#"):
            print(linea)
            continue

        if linea.startswith("timestamp_ms"):
            header = linea.split(",")
            print("\nCSV detectado correctamente.")
            print("Columnas:")
            for col in header:
                print(f" - {col}")
            print()
            continue

        if header and "," in linea:
            partes = linea.split(",")

            if len(partes) != len(header):
                print("Línea ignorada:")
                print(linea)
                continue

            lineas.append(partes)
            dato = dict(zip(header, partes))

            os.system("cls" if os.name == "nt" else "clear")

            print("======================================")
            print(" MACETA INTELIGENTE - LECTURA ACTUAL")
            print("======================================")
            print(f"Muestra: {len(lineas)} / {MAX_MUESTRAS}")
            print(f"Tiempo ESP32: {dato['timestamp_ms']} ms")

            print("\n----------- HUMEDAD DE SUELO -----------")
            print(f"Sensor suelo 1: {dato['soil1_raw']} RAW | {dato['soil1_v']} V")
            print(f"Sensor suelo 2: {dato['soil2_raw']} RAW | {dato['soil2_v']} V")
            print(f"Promedio suelo: {dato['soil_avg_raw']} RAW")

            print("\n----------- RADIACIÓN UV -----------")
            print(f"GUVA-S12SD: {dato['uv_raw']} RAW | {dato['uv_v']} V")

            print("\n----------- INTENSIDAD LUMINICA -----------")
            print(f"BH1750: {dato['lux']} lux")

            print("\n----------- ACTUADORES -----------")
            print(f"Bomba: {'ENCENDIDA' if dato['pump_state'] == '1' else 'APAGADA'}")
            print(f"LEDs: {'ENCENDIDOS' if dato['leds_state'] == '1' else 'APAGADOS'}")

            print("\n======================================")

except KeyboardInterrupt:
    print("\nCaptura detenida manualmente con Ctrl+C.")

finally:
    if ser.is_open:
        ser.close()

if not lineas:
    print("\nNo se recibieron datos válidos.")
    sys.exit()

# =======================
# CREAR CSV
# =======================
df = pd.DataFrame(lineas, columns=header)

for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_csv(ARCHIVO_CSV, index=False)
print(f"\nCSV guardado correctamente: {ARCHIVO_CSV}")

# =======================
# GRÁFICA HUMEDAD DE SUELO
# =======================
plt.figure()
plt.plot(df["timestamp_ms"], df["soil1_raw"], label="Humedad suelo 1")
plt.plot(df["timestamp_ms"], df["soil2_raw"], label="Humedad suelo 2")
plt.plot(df["timestamp_ms"], df["soil_avg_raw"], label="Promedio suelo")
plt.xlabel("Tiempo (ms)")
plt.ylabel("ADC RAW")
plt.title("Humedad de suelo")
plt.legend()
plt.grid(True)
plt.savefig("grafica_humedad_suelo.png", dpi=300)
plt.show()

# =======================
# GRÁFICA UV
# =======================
plt.figure()
plt.plot(df["timestamp_ms"], df["uv_raw"])
plt.xlabel("Tiempo (ms)")
plt.ylabel("ADC RAW")
plt.title("Radiación UV GUVA-S12SD")
plt.grid(True)
plt.savefig("grafica_uv.png", dpi=300)
plt.show()

# =======================
# GRÁFICA LUZ
# =======================
plt.figure()
plt.plot(df["timestamp_ms"], df["lux"])
plt.xlabel("Tiempo (ms)")
plt.ylabel("Lux")
plt.title("Intensidad luminica BH1750")
plt.grid(True)
plt.savefig("grafica_lux.png", dpi=300)
plt.show()

# =======================
# GRÁFICA ACTUADORES
# =======================
plt.figure()
plt.plot(df["timestamp_ms"], df["pump_state"], label="Bomba")
plt.plot(df["timestamp_ms"], df["leds_state"], label="LEDs")
plt.xlabel("Tiempo (ms)")
plt.ylabel("Estado 0/1")
plt.title("Estado de actuadores")
plt.legend()
plt.grid(True)
plt.savefig("grafica_actuadores.png", dpi=300)
plt.show()

print("\nARCHIVOS GENERADOS:")
print(f"- {ARCHIVO_CSV}")
print("- grafica_humedad_suelo.png")
print("- grafica_uv.png")
print("- grafica_lux.png")
print("- grafica_actuadores.png")