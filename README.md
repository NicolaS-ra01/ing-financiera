Aplicativo de Tabla de Amortización en Python

Este proyecto implementa un aplicativo financiero utilizando Python y la librería tkinter (ttk) para generar una Tabla de Amortización bajo el sistema de cuota constante (Sistema Francés).

Su objetivo es demostrar la correcta aplicación de conceptos financieros avanzados, incluyendo la conversión de tasas y la gestión de abonos extraordinarios con re-cálculo automático.

  Requisitos y Ejecución

    Requisitos: Python 3.6+ (o superior) con la librería estándar tkinter y la librería csv.

    Archivos: Asegúrese de tener main_app.py y financiero.py en el mismo directorio.

    Ejecución: Abra una terminal (CMD o PowerShell) en el directorio del proyecto y ejecute:
    Bash

    python main_app.py

 Guía de Uso del Aplicativo

1. Ingreso de Parámetros Iniciales

Complete los campos en la sección "Parámetros del Crédito":
Campo	Descripción	Formato de Entrada
Monto Crédito ($)	El capital o principal del préstamo.	Numérico (ej: 10000)
Tasa Anual (%)	Tasa de interés anual (ej: 12 para 12%).	Numérico (ej: 12.5)
Plazo (períodos totales)	El número total de pagos (cuotas).	Entero (ej: 36)
Frecuencia Pago	Seleccione la periodicidad del pago (Mensual, Quincenal, etc.).	Selección (ej: Mensual (12))
Tipo de Tasa	Define la naturaleza de la Tasa Anual ingresada.	Selección (NOMINAL, EFECTIVA, ANTICIPADA)

Una vez completados, presione "Generar Tabla". La cuota constante se calculará y se mostrará la tabla.

2. Aplicación de Abonos Extraordinarios

Use la sección "Acciones" para gestionar pagos adicionales (ad-hoc):

    Ingrese el Período Abono (número de la fila donde se realizará el pago extra).

    Ingrese el Monto ($) del abono extraordinario.

    Seleccione la opción de re-cálculo:

        Reducir Plazo: Mantiene la cuota original y acorta el tiempo del crédito.

        Reducir Cuota: Mantiene el plazo original y disminuye el valor de la cuota restante.

    Presione "Aplicar Abono". La tabla se actualizará automáticamente.

3. Exportar Resultados

Presione "Exportar a CSV" para guardar la tabla final (incluyendo abonos y re-cálculos) en un archivo .csv para su verificación.
