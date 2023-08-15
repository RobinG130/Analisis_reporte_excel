import pandas as pd
from tkinter import Tk, filedialog, messagebox, ttk
import matplotlib.pyplot as plt
import tkinter as tk
import matplotlib.colors as mcolors
import matplotlib.cm as cm

raw_df = None
available_dates = []

def print_output(output):

    output_text.insert(tk.END, output + "\n")
    output_text.insert(tk.END, "\n")
    output_text.see(tk.END)  # Scroll to the end

def combinar_archivos():
    files = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=(("Archivos XLSX y CSV", "*.xlsx; *.csv"), ("Todos los archivos", "*.*")))
    header_values = ['Date', 'time', 'user1', 'user2', 'wo', 'model', 'station', 'pallet', 'slot', 'off', 'offv', 'offpf',
                     'offll', 'offul', 'offvo', 'offvex', 'out', 'outv', 'outpf', 'outll', 'outul', 'outocv', 'outccv',
                     'outrl', 'outp100', 'Hys', 'hysv', 'hyspf', 'hysll', 'hysul', 'hysvo2', 'hysvo1', 'hysv1', 'p300',
                     'Sen', 'senv', 'senpf', 'senll', 'senul', 'senvh', 'senoff', 'senvex', 'senvhp', 'Lin', 'linv',
                     'linpf', 'linll', 'linul', 'linvf', 'linvo', 'linvhp', 'linvfp', 'linvh', 'Cal', 'calv', 'calpf',
                     'call', 'calul', 'calvc', 'calvo', 'calvh', 'Flr', 'flrv', 'flrpf', 'flrll', 'flrul', 'flrvex10',
                     'Pos', 'posv', 'pospf', 'posll', 'posul', 'Blr', 'blrv', 'blrpf', 'blrll', 'blrul', 'Neg', 'negv',
                     'negpf', 'negll', 'negul', 'Imp', 'impv', 'imppf', 'impll', 'impul', 'Gnd', 'gndv', 'gndpf',
                     'gndll', 'gndul', 'gnd45', 'Cap', 'capv', 'cappf', 'capll', 'capul', 'Dis', 'disv', 'dispf',
                     'disll', 'disul', 'Flo', 'flov', 'flopf', 'floll', 'floul']

    if files:
        dataframe = []
        for file in files:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.endswith('.csv'):
                df = pd.read_csv(file, header=None, delimiter=",")
                df.columns = header_values
            dataframe.append(df)

        combined_df = pd.concat(dataframe)

        combined_df['Resultado'] = combined_df['offpf'] * combined_df['outpf'] * combined_df['hyspf'] * combined_df['linpf'] * combined_df['flrpf'] * combined_df['pospf'] * combined_df['blrpf'] * combined_df['negpf'] * combined_df['imppf'] * combined_df['gndpf']

        print_output("El DataFrame combinado:\n")
        print_output(str(combined_df))

        combined_df.to_csv("combined.csv", index=False)

        global available_dates
        available_dates = obtener_fechas_disponibles(combined_df)  # Update the available dates for the Listbox

        # Update the values of the date_listbox
        date_listbox.delete(0, tk.END)
        for date in available_dates:
            date_listbox.insert(tk.END, date)

        return combined_df

    else:
        print_output("No se seleccionaron archivos.")
        return None

def crear_df():
    global raw_df
    raw_df = combinar_archivos()

    if raw_df is not None:
        print_output("DataFrame obtenido correctamente")
    else:
        print_output("Error al obtener el DataFrame")

    # Update the column_option dropdown list with the display values
    column_option['values'] = column_options[1:]  # Exclude the first empty option

def prueba_individuales(df):
    column_names = {
        'offpf': 'Offset',
        'outpf': 'Output_imp',
        'hyspf': 'Hysteresis',
        'linpf': 'Linearity',
        'flrpf': 'Front_leak',
        'pospf': 'Volt_pos',
        'blrpf': 'Backside_leak',
        'negpf': 'Volt_neg',
        'imppf': 'Input Impedance',
        'gndpf': 'Ground'
    }

    fallas = df[['offpf', 'outpf', 'hyspf', 'linpf', 'flrpf', 'pospf', 'blrpf', 'negpf', 'imppf', 'gndpf']].eq(0).sum()
    fallas = fallas.rename(column_names)
    fallas_ordenadas = fallas.sort_values(ascending=False)
    return fallas_ordenadas

def fallas_por_puerto(dataframe):
    unidades_falladas = {
        'Port 1': 0,
        'Port 2': 0,
        'Port 3': 0,
        'Port 4': 0,
        'Port 5': 0,
        'Port 6': 0
    }

    for index, row in dataframe.iterrows():
        station = row['station']
        slot = row['slot']
        resultado = row['Resultado']

        if resultado == 0:
            if station == 1:
                if slot == 1:
                    unidades_falladas['Port 1'] += 1
                elif slot == 2:
                    unidades_falladas['Port 2'] += 1
            elif station == 2:
                if slot == 1:
                    unidades_falladas['Port 3'] += 1
                elif slot == 2:
                    unidades_falladas['Port 4'] += 1
            elif station == 3:
                if slot == 1:
                    unidades_falladas['Port 5'] += 1
                elif slot == 2:
                    unidades_falladas['Port 6'] += 1

    series_fallas = pd.Series(unidades_falladas)
    return series_fallas

def grafico_barras(pandas_series, title, alpha=0.3):
    plt.figure(figsize=(4.5, 2.5))
    colors = [(1.0, 0.0, 0.0, alpha),   # Red
              (0.0, 1.0, 0.0, alpha),   # Green
              (0.0, 0.0, 1.0, alpha),   # Blue
              (1.0, 1.0, 0.0, alpha),   # Yellow
              (1.0, 0.0, 1.0, alpha),   # Magenta
              (0.0, 1.0, 1.0, alpha)]   # Cyan
    pandas_series.plot(kind='bar', color=colors)
    for i, valor in enumerate(pandas_series):
        plt.text(i, valor, str(valor), ha='center', va='bottom')

    plt.title(title)
    if len(pandas_series) > 6:
        plt.xticks(rotation=90)
    else:
        plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

def cal_yield(df):
    val_yield = (df['Resultado'] == 1).sum() / len(df['Resultado'])
    return round(val_yield * 100, 2)

def obtener_fechas_disponibles(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    fechas_disponibles = df['Date'].dt.strftime('%m/%d/%Y').unique()
    return fechas_disponibles

def fallas_por_paleta(df):
    df_fallas = df[df['Resultado'] == 0].copy()
    df_fallas['palletas'] = df_fallas['pallet'].str[:3]
    conteo_pallets = df_fallas['palletas'].value_counts()
    return conteo_pallets.sort_values(ascending=False)

def analizar_data():
    if raw_df is not None:
        selected_column_display = column_option.get()  # Get the selected display value from the dropdown list
        
        column_mapping = {
            'Offset': 'offpf',
            'Output imp': 'outpf',
            'Hysteresis': 'hyspf',
            'Linearity': 'linpf',
            'Front leak': 'flrpf',
            'Volt pos': 'pospf',
            'Backside leak': 'blrpf',
            'Volt neg': 'negpf',
            'Input Impedance': 'imppf',
            'Ground': 'gndpf'
        }
        
        selected_column = column_mapping.get(selected_column_display)  # Get the corresponding internal column name 
        selected_dates = date_listbox.curselection()  # Get the indices of selected dates from the Listbox

        # Check if any date is selected
        if not selected_dates:
            messagebox.showwarning("Error", "Por favor, seleccione al menos una fecha.")
            return

        selected_dates = [date_listbox.get(index) for index in selected_dates]  # Get the actual selected dates
        filtered_df = raw_df[raw_df['Date'].isin(selected_dates)]  # Filter the raw_df based on the selected dates

        print_output("Unidades falladas por paleta:")
        print_output(str(fallas_por_paleta(filtered_df)).split("Name")[0])

        print_output("Top Offenders:")
        print_output(str(prueba_individuales(filtered_df)).split("dtype")[0])

        print_output("Fallas por puerto:")
        print_output(str(fallas_por_puerto(filtered_df)).split("dtype")[0])
                       
        yield_value = cal_yield(filtered_df)
        yield_text.delete('1.0', tk.END)  # Clear previous yield value
        yield_text.insert(tk.END, str(yield_value) + "%")  # Update yield value in the Text widget

        print_output("Yield:")
        print_output(str(yield_value) + "%")
        
        grafico_barras(fallas_por_puerto(filtered_df), "Fallas por Puerto")
        grafico_barras(prueba_individuales(filtered_df), "Top Offenders")
        grafico_barras(fallas_por_paleta(filtered_df), "Fallas por Paleta")
        
        #Show total processed  units
        print_output("Total de unidades procesadas:")
        print_output(str(len(filtered_df['Resultado']))+ " unidades")

        if selected_column in filtered_df.columns:
            if (filtered_df[selected_column] == 0).any():
                fallas_filtradas = fallas_por_puerto(filtered_df[filtered_df[selected_column] == 0])
                grafico_barras(fallas_filtradas, f"Unidades falladas por {selected_column_display}")

                print_output(f"Unidades falladas por {selected_column_display}:")        
                print_output(str(fallas_filtradas).split("dtype")[0])

            else:
                print_output("No se encontraron unidades falladas para la prueba seleccionada.")
        else:
            print_output("Selecciona una prueba individual para graficar.")
  
    else:
        print_output("Seleccione archivos para analizar")


#GUI
#titulo de la ventana principal
main_window = tk.Tk()
main_window.title("Analizar Data de Pruebas FET")

output_text = tk.Text(main_window)
output_text.pack(fill=tk.BOTH, expand=True)

# Label for the dropdown list
label_prueba = tk.Label(main_window, text="Seleccione una prueba para analizar")
label_prueba.pack()

# Update the column_options list to contain the display values
column_options = ["", 'Offset', 'Output imp', 'Hysteresis', 'Linearity', 'Front leak', 'Volt pos', 'Backside leak', 'Volt neg', 'Input Impedance', 'Ground']

# Create a Combobox for column selection
column_option = ttk.Combobox(main_window, values=column_options)
column_option.current(0)  # Set the initial selected column
column_option.pack()

# Label for the date list
label_fecha = tk.Label(main_window, text="Seleccione una fecha para mostrar")
label_fecha.pack()

# Create a Listbox for date selection
date_listbox = tk.Listbox(main_window, selectmode=tk.MULTIPLE)
date_listbox.pack()

button_obtener_df = tk.Button(main_window, text="Seleccionar Archivos", command=crear_df)
button_analizar = tk.Button(main_window, text="Analizar Data", command=analizar_data)

button_analizar.pack()
button_obtener_df.pack()

# Exit button
button_salir = tk.Button(main_window, text="Salir", command=main_window.quit)
button_salir.pack()

# Label and Text widget for yield value
yield_text = tk.Text(main_window, height=1, width=6)
yield_text.pack(side=tk.RIGHT)

yield_label = tk.Label(main_window, text="Yield:")
yield_label.pack(side=tk.RIGHT)

main_window.mainloop()
