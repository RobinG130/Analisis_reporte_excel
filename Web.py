import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import calendar 

#configurar el header de la Pagina
st.set_page_config(page_title="Analysis of Metrics",
                   page_icon="🚀",
                   )
st.title("Downtime Analysis 📊")
st.subheader("Upload a file to analyze")

#Area de sidebar pata filtrar
st.sidebar.header("Selecciones los parametros para filtrar")

#Hacer unmerged de las columnas para que se lea correctamente la fecha
def unmerge_dataframe_cells(dataframe):
    for column in dataframe.columns:
        for index, cell_value in enumerate(dataframe[column]):
            if isinstance(cell_value, str) and '\n' in cell_value:
                split_values = cell_value.split('\n')
                dataframe.at[index, column] = split_values[0]

# Función para convertir tiempo en formato HH:MM a minutos
def convert_to_minutes(time_str):
    if pd.notna(time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    return 0

# Función para convertir minutos a tiempo en formato HH:MM
def convert_to_time_format(minutes):
    hours = minutes // 60
    minutes %= 60
    return f"{hours:02d}:{minutes:02d}"

#cargar el archivo y limpiar la data
uploaded_file = st.file_uploader("Select a file to analyze", type=["xls","xlsx", "csv"])

if uploaded_file:
    st.markdown("---")
    expected_dtypes = {
    'Work Order': 'str',
    'WO Description': 'str',
    'Asset': 'category',
    'Asset Description': 'str',
    'Old ID': 'str',
    'Location': 'category',
    'Loc Description': 'str',
    'Asset Department': 'category',
    'Criticallity': 'category',
    'Classification': 'category',
    'Asset Status': 'category',
    'Reported Date': 'datetime64[ns]',
    'Reported By': 'str',
    'Actual Finish': 'datetime64[ns]',
    'WO Status': 'category',
    'Status Date': 'datetime64[ns]',
    'Work Type': 'category'
    }

    #Se usa try para manejar errores si no se entrega el archivo con el formato esperado
    try:
        #Leer y limpiar la data
        df = pd.read_excel(uploaded_file, sheet_name='Report', skiprows=2, skipfooter=5, parse_dates=True, engine="openpyxl",dtype=expected_dtypes)
        unmerge_dataframe_cells(df)
        columns_to_drop = [2, 6, 10, 11, 13, 27, 28, 29, 30]
        df = df.drop(df.columns[columns_to_drop], axis=1)
        df.dropna(subset=['Asset'], inplace=True)
        df["Month"] = df["Reported Date"].dt.month.apply(lambda x: calendar.month_name[x])  # Get month names
        ########
        ###Filtrar###
                   
      #worktype
        work_types = st.sidebar.multiselect(
        "Selecione tipo de Work Order:",
        options=df["Work Type"].unique(),
        default=["CM", "ER"]
        )
  
         #ValueStream
        valuestream = st.sidebar.multiselect(
        "Selecione el Value Stream:",
        options=df["Asset Department"].unique(),
        default=["Manufacturing SubAssy", "Manufacturing HV", "Manufacturing SG", "Manufacturing SR - Surgical Recovery", "Manufacturing LV"]
        )
       
        df = df.query("`Work Type` in @work_types and `Asset Department` in @valuestream")

       
        ########
        st.dataframe(df)
        
        if not df.empty:  # verificar que el DataFrame no esté vacío   

            # Convertir las horas a minutos y luego sumar
            df["Actual Labor Hours (in minutes)"] = df["Actual Labor Hours"].apply(convert_to_minutes)
            total_minutes = df["Actual Labor Hours (in minutes)"].sum()
            total_time_formatted = convert_to_time_format(total_minutes)
            grouped_df=df.groupby("Asset")["Actual Labor Hours (in minutes)"].sum().reset_index()
            st.dataframe(grouped_df)
            st.write(f"Totallllllll Actual Labor Hours: {total_time_formatted}")

            #Grafico de barras de downtime por asset
            #grouped_df["Asset"] = grouped_df["Asset"].astype(str)  # Mantener el tipo de dato como str
            
            grouped_df = grouped_df.sort_values("Actual Labor Hours (in minutes)", ascending=False).head(5)

            plt.figure(figsize=(10, 6))
            plt.bar(grouped_df["Asset"], grouped_df["Actual Labor Hours (in minutes)"])
            plt.xlabel("Asset")
            plt.ylabel("Total Actual Labor Hours (in minutes)")
            plt.title("Total Actual Labor Hours by Asset")
            plt.xticks(rotation=45)
            st.pyplot(plt)
           
            ####Grafica de downtime por mes
            grouped_df=df.groupby("Month")["Actual Labor Hours (in minutes)"].sum().reset_index()
            grouped_df = grouped_df.sort_values("Month")
            st.dataframe(grouped_df)
            fig2 = px.bar(grouped_df, x="Month", y="Actual Labor Hours (in minutes)",
            labels={"Month": "Mes", "Actual Labor Hours (in minutes)": "Downtime Acumulado (in minutes)"},             
            title="Total downtime por Mes")
            fig2.update_xaxes(tickangle=45)
            fig2.update_traces(text=grouped_df["Actual Labor Hours (in minutes)"], textposition="outside")
            st.plotly_chart(fig2)
            ####

    except Exception as e:
        st.error(f"An error occurred: {e}")

    st.markdown("---")
