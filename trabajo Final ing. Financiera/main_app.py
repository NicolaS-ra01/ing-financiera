import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
from typing import List, Dict
import financiero # Importamos nuestro módulo de cálculos

# --- Diccionario de Frecuencias Estándar ---
FRECUENCIAS_ANUALES = {
    "Mensual (12)": 12,
    "Quincenal (24)": 24,
    "Bimestral (6)": 6,
    "Trimestral (4)": 4,
    "Semestral (2)": 2,
    "Anual (1)": 1,
    "Semanal (52)": 52,
}
# ---------------------------------------------

class AmortizacionApp:
    def __init__(self, master):
        self.master = master
        master.title("Aplicativo de Tabla de Amortización (Python/ttk)")
        
        # Variables de entrada
        self.monto = tk.DoubleVar()
        self.tasa = tk.DoubleVar()
        self.plazo = tk.IntVar()
        self.frecuencia_nombre = tk.StringVar(value="Mensual (12)") 
        self.tipo_tasa = tk.StringVar(value="NOMINAL")
        self.fecha_inicio = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        # Estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        self.tabla_amortizacion: List[Dict] = []
        self.tasa_per = 0.0
        self.cuota_original = 0.0

        # Crear la interfaz
        self.crear_widgets_parametros()
        self.crear_widgets_tabla()
        self.crear_widgets_acciones()

    # --- 1. Widgets de Entrada de Parámetros ---
    def crear_widgets_parametros(self):
        frame_params = ttk.LabelFrame(self.master, text="  Parámetros del Crédito  ")
        frame_params.pack(padx=10, pady=10, fill="x")

        labels = ["Monto Crédito ($):", "Tasa Anual (%):", "Plazo (períodos totales):", "Frecuencia Pago:", "Tipo de Tasa:"]
        vars_list = [self.monto, self.tasa, self.plazo, self.frecuencia_nombre, self.tipo_tasa]
        
        for i, label_text in enumerate(labels):
            label = ttk.Label(frame_params, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=3, sticky="w")
            
            if i in [0, 1, 2]: # Monto, Tasa, Plazo (Entry)
                entry = ttk.Entry(frame_params, textvariable=vars_list[i], width=15)
                entry.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            elif i == 3: # Frecuencia Pago (Combobox)
                combo = ttk.Combobox(frame_params, textvariable=vars_list[i], values=list(FRECUENCIAS_ANUALES.keys()), width=13, state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            else: # Tipo de Tasa (Combobox)
                combo = ttk.Combobox(frame_params, textvariable=vars_list[i], values=["NOMINAL", "EFECTIVA", "ANTICIPADA"], width=13, state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=3, sticky="ew")

        # Botón para Generar Tabla
        btn_generar = ttk.Button(frame_params, text="Generar Tabla", command=self.generar_tabla)
        btn_generar.grid(row=0, column=2, rowspan=5, padx=10, pady=5, sticky="ns")

    # --- 2. Widgets de la Tabla de Amortización (Treeview) ---
    def crear_widgets_tabla(self):
        frame_tabla = ttk.LabelFrame(self.master, text="  Tabla de Amortización  ")
        frame_tabla.pack(padx=10, pady=5, fill="both", expand=True)

        # Definir Columnas
        columnas = ('periodo', 'fecha', 'saldo_inicial', 'interes', 'cuota_pagada', 'amortizacion', 'abono_adhoc', 'saldo_final')
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        # Configurar Encabezados
        for col in columnas:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, anchor='center', width=100)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

        self.tree.pack(fill="both", expand=True)
    
    # --- 3. Widgets de Abonos y Acciones ---
    def crear_widgets_acciones(self):
        frame_acciones = ttk.LabelFrame(self.master, text="  Acciones  ")
        frame_acciones.pack(padx=10, pady=10, fill="x")

        # Sección Abonos
        ttk.Label(frame_acciones, text="Período Abono:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.abono_periodo = ttk.Entry(frame_acciones, width=8)
        self.abono_periodo.grid(row=0, column=1, padx=5, pady=3, sticky="w")
        
        ttk.Label(frame_acciones, text="Monto ($):").grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.abono_monto = ttk.Entry(frame_acciones, width=10)
        self.abono_monto.grid(row=0, column=3, padx=5, pady=3, sticky="w")
        
        # Opciones de Recálculo
        self.opcion_recalculo = tk.StringVar(value="PLAZO")
        ttk.Radiobutton(frame_acciones, text="Reducir Plazo", variable=self.opcion_recalculo, value="PLAZO").grid(row=0, column=4, padx=10, pady=3)
        ttk.Radiobutton(frame_acciones, text="Reducir Cuota", variable=self.opcion_recalculo, value="CUOTA").grid(row=0, column=5, padx=10, pady=3)
        
        btn_abono = ttk.Button(frame_acciones, text="Aplicar Abono", command=self.aplicar_abono)
        btn_abono.grid(row=0, column=6, padx=10, pady=5)
        
        # Sección Exportar
        btn_exportar = ttk.Button(frame_acciones, text="Exportar a CSV", command=self.exportar_csv)
        btn_exportar.grid(row=0, column=7, padx=10, pady=5)
    
    # --- Funcionalidad ---

    def validar_entradas(self):
        """Valida que los inputs sean válidos y retorna los valores ajustados."""
        try:
            monto = self.monto.get()
            tasa_porcentual = self.tasa.get()
            plazo = self.plazo.get()
            
            # **Ajuste clave:** Convertir el porcentaje (ej: 10) a factor (ej: 0.10)
            tasa = tasa_porcentual / 100.0 
            
            # Obtener el número de períodos al año desde el diccionario
            frecuencia_nombre = self.frecuencia_nombre.get()
            frecuencia = FRECUENCIAS_ANUALES[frecuencia_nombre]
            
            fecha_inicio_dt = date.fromisoformat(self.fecha_inicio.get())
            
            if monto <= 0 or tasa_porcentual <= 0 or plazo <= 0 or frecuencia <= 0:
                raise ValueError("Todos los valores deben ser positivos.")
                
            return monto, tasa, plazo, frecuencia, fecha_inicio_dt
        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Error de formato o valor: {e}\nAsegúrese de usar números válidos y una fecha YYYY-MM-DD.")
            return None

    def generar_tabla(self):
        """Llama a la lógica financiera y muestra la tabla."""
        params = self.validar_entradas()
        if not params: return

        monto, tasa, plazo, frecuencia, fecha_inicio_dt = params
        
        # 1. Calcular la Tasa Efectiva Periódica
        try:
            self.tasa_per = financiero.calcular_tasa_periodica(tasa, frecuencia, self.tipo_tasa.get())
        except ValueError as e:
            messagebox.showerror("Error Financiero", str(e))
            return
            
        # 2. Calcular la Cuota Constante
        self.cuota_original = financiero.calcular_cuota_constante(monto, self.tasa_per, plazo)

        # 3. Generar la Tabla
        try:
            self.tabla_amortizacion = financiero.generar_tabla_base(
                monto, self.tasa_per, self.cuota_original, plazo, frecuencia, fecha_inicio_dt
            )
            self.actualizar_treeview()
            messagebox.showinfo("Éxito", f"Tabla generada.\nCuota constante: ${self.cuota_original:,.2f}\nTasa periódica: {self.tasa_per*100:,.4f}%")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Ocurrió un error al generar la tabla: {e}")

    def aplicar_abono(self):
        """Aplica el abono y llama a la función de re-cálculo."""
        if not self.tabla_amortizacion:
            messagebox.showwarning("Advertencia", "Primero genere la tabla de amortización.")
            return
            
        try:
            periodo = int(self.abono_periodo.get())
            monto = float(self.abono_monto.get())
            opcion = self.opcion_recalculo.get()
            
            if periodo <= 0 or monto <= 0:
                raise ValueError("El período y el monto del abono deben ser positivos.")

            plazo_original = self.plazo.get()
            frecuencia = FRECUENCIAS_ANUALES[self.frecuencia_nombre.get()]

            self.tabla_amortizacion = financiero.aplicar_abono_y_recalcular(
                self.tabla_amortizacion, periodo, monto, opcion, self.tasa_per, plazo_original, frecuencia
            )
            self.actualizar_treeview()
            messagebox.showinfo("Abono Aplicado", f"Abono de ${monto:,.2f} aplicado en período {periodo}. Tabla recalculada para reducir {opcion.lower()}.")

        except Exception as e:
            messagebox.showerror("Error al Aplicar Abono", f"Error: {e}")

    def actualizar_treeview(self):
        """Limpia el Treeview y lo llena con los datos de la tabla."""
        # Limpiar entradas previas
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Insertar nuevas filas
        for fila in self.tabla_amortizacion:
            # Resaltar la fila de abono o la fila de re-cálculo
            tags = ()
            if fila.get('abono_adhoc', 0.0) > 0.0:
                tags = ('abono',)
            elif fila.get('recalculado', False) and fila['periodo'] > 1:
                tags = ('recalculado',)
                
            values = [f"{fila['periodo']:}", 
                      fila['fecha'],
                      f"{fila['saldo_inicial']:,.2f}",
                      f"{fila['interes']:,.2f}",
                      f"{fila['cuota_pagada']:,.2f}",
                      f"{fila['amortizacion']:,.2f}",
                      f"{fila['abono_adhoc']:,.2f}",
                      f"{fila['saldo_final']:,.2f}"]
                      
            self.tree.insert('', tk.END, values=values, tags=tags)

        # Configurar tags de estilo (ttk)
        self.tree.tag_configure('abono', background='#e0ffff', font=('Arial', 9, 'bold')) # Azul claro para abono
        self.tree.tag_configure('recalculado', background='#fffacd') # Amarillo claro para filas recalculadas

    def exportar_csv(self):
        """Permite al usuario elegir la ubicación y exporta la tabla."""
        if not self.tabla_amortizacion:
            messagebox.showwarning("Advertencia", "Primero genere la tabla de amortización para exportar.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                mensaje = financiero.exportar_tabla_csv(self.tabla_amortizacion, file_path)
                messagebox.showinfo("Exportación Exitosa", mensaje)
            except Exception as e:
                messagebox.showerror("Error de Exportación", f"No se pudo exportar el archivo: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = AmortizacionApp(root)
    root.mainloop()