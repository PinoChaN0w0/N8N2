import os
import sys
import json
import time
import glob
import shutil
import tempfile
import subprocess
import ctypes
import pyautogui
import pygetwindow as gw

# Configuración de PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.5

# --- LOGGING SEPARADO ---
def log(msg):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_PBIX = os.path.join(BASE_DIR, "Reporte.pbix")
NOMBRE_PDF = "Reporte.pdf"
RUTA_PDF = os.path.join(BASE_DIR, NOMBRE_PDF)

user32 = ctypes.windll.user32


def buscar_pdf_en_temp(inicio_tiempo=None):
    """Busca el archivo PDF generado automáticamente en Temp."""
    temp_pbi = os.path.join(tempfile.gettempdir(), "Power BI Desktop")
    if not os.path.exists(temp_pbi):
        return None

    candidatos = []
    # CORREGIDO: Sintaxis de glob con wildcard recursivo
    patron = os.path.join(temp_pbi, "**", "*.pdf")
    for archivo in glob.glob(patron, recursive=True):
        try:
            mtime = os.path.getmtime(archivo)
            size = os.path.getsize(archivo)
            if size > 0:
                if inicio_tiempo is None or mtime >= (inicio_tiempo - 10):
                    candidatos.append((mtime, archivo))
        except OSError:
            continue

    if not candidatos:
        return None

    candidatos.sort(key=lambda x: x[0], reverse=True)
    return candidatos[0][1]

def exportar_powerbi():
    # 0. Limpieza inicial
    if os.path.exists(RUTA_PDF):
        try:
            os.remove(RUTA_PDF)
            log(f"Archivo previo eliminado en destino: {RUTA_PDF}")
        except Exception as e:
            log(f"Aviso al limpiar PDF previo: {e}")

    if not os.path.exists(RUTA_PBIX):
        raise FileNotFoundError(f"No se encontró el archivo del reporte en: {RUTA_PBIX}")

    # 1. Abrir Power BI Desktop
    log(f"Abriendo Power BI con: {RUTA_PBIX}...")
    proc = subprocess.Popen([RUTA_PBIX], shell=True)

    log("Esperando a que la ventana de Power BI se inicialice...")    
    # Tiempo para carga completa del informe
    time.sleep(15)

    

    # 2. Exportación mediante menú de acceso rápido de teclado (sin clics de mouse)
    log("Ejecutando secuencia de exportación a PDF...")
    # NAVEGACIÓN TECLADO: Archivo -> Exportar -> Exportar a PDF
    pyautogui.moveTo(30, 50)    # Abre menú Archivo
    time.sleep(1)
    log("moviendo1")
    pyautogui.click()
    pyautogui.moveTo(87, 406)
    log("moviendo2")
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(300, 200)
    pyautogui.click()
    time.sleep(1)
    log("moviendo3")

    # 3. Espera de generación del PDF
    log("Esperando a que Power BI genere el archivo PDF...")
    pdf_origen = None
    timeout_pdf = 60
    inicio_pdf = time.time()
    inicio_exportacion = time.time()
    temp_pdf = buscar_pdf_en_temp(inicio_exportacion)
    pdf_origen = temp_pdf
   

    if not pdf_origen:
        raise TimeoutError(f"No se detectó el archivo PDF generado en el tiempo esperado ({timeout_pdf}s).")

    log(f"PDF detectado en: {pdf_origen}. Verificando finalización de escritura...")

    
    # 3. Copiar al destino final
    if os.path.abspath(pdf_origen) != os.path.abspath(RUTA_PDF):
        log(f"Copiando PDF desde '{pdf_origen}' hacia '{RUTA_PDF}'...")
        shutil.copy2(pdf_origen, RUTA_PDF)
        if not os.path.exists(RUTA_PDF) or os.path.getsize(RUTA_PDF) == 0:
            raise IOError(f"No se pudo completar la copia del PDF a la ruta final: {RUTA_PDF}")

    # 4. Cierre limpio
    log("Cerrando Power BI Desktop...")
    pyautogui.hotkey('alt', 'f4')
    time.sleep(2)

    # 5. Retorno de JSON para n8n
    return {
        "status": "success",
        "file_name": NOMBRE_PDF,
        "file_path": RUTA_PDF,
        "folder": BASE_DIR,
        "temp_source_path": pdf_origen if os.path.abspath(pdf_origen) != os.path.abspath(RUTA_PDF) else None,
        "file_size_bytes": os.path.getsize(RUTA_PDF),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

if __name__ == "__main__":
    try:
        resultado = exportar_powerbi()
        print(json.dumps(resultado, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        resultado_error = {
            "status": "error",
            "message": str(e),
            "file_path": None
        }
        print(json.dumps(resultado_error, ensure_ascii=False))
        sys.exit(1)