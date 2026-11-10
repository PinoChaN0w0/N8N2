import pyautogui
import time

try:
    print("Mueve el cursor sobre la pantalla (Presiona Ctrl + C para salir):")
    while True:
        # Obtiene la posición actual del cursor (X, Y)
        x, y = pyautogui.position()
       
        # .ljust(35) limpia los caracteres residuales que deja '\r' al imprimir números más cortos
        texto = f"X: {x} | Y: {y}"
        print(texto.ljust(35), end="\r", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nTerminado.")