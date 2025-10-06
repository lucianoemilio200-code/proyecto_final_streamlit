import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# función donde se se inicializa y controla la variable session_state
def inicializar_session_state():
    if 'df_limpio' not in st.session_state:
        st.session_state.df_limpio = None
    if 'archivo_cargado' not in st.session_state:
        st.session_state.archivo_cargado = False
    if 'accion_solicitada' not in st.session_state:
        st.session_state.accion_solicitada = False
    if 'analisis_seleccionado' not in st.session_state:
        st.session_state.analisis_seleccionado = "Ver resumen del dataset"
    if 'nulos_eliminados' not in st.session_state: 
        st.session_state.nulos_eliminados = 0
    if 'duplicados_eliminados' not in st.session_state:
        st.session_state.duplicados_eliminados = 0

inicializar_session_state()

st.set_page_config(layout="wide", page_title="Aplicación para visualización de Datos")
st.title("📊 Aplicación para visualización de Datos") 

@st.cache_data
# función para cargar los datos de los archivos csv y excel
def cargar_limpiar_datos(archivo_subido):
    try:
        #Valida que el tipo de archivo sea válido
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(io.StringIO(archivo_subido.getvalue().decode('utf-8')))
        elif archivo_subido.name.endswith('.xlsx'):
            df = pd.read_excel(archivo_subido)
        else:
            return None, "Error: El formato del archivo no es válido", 0, 0 

        # Se quitan las filas con valores nulos
        filas_antes_nullos = len(df)
        df = df.dropna()
        nulos_eliminados = filas_antes_nullos - len(df)

        # Se intenta convertir a datos numericos las columnas que se puedan
        for columna in df.select_dtypes(include=['object']).columns:
            columna_temporal = pd.to_numeric(df[columna], errors='coerce')
            if columna_temporal.isnull().sum() < df[columna].isnull().sum() or columna_temporal.isnull().sum() == 0:
                df[columna] = columna_temporal
        
        # Se quitan los valores duplicados del dataset
        filas_antes_duplicados = len(df) 
        df = df.drop_duplicates().copy()
        duplicados_eliminados = filas_antes_duplicados - len(df)
        
        st.success(f"Carga y Limpieza exitosa.\n Se eliminaron {nulos_eliminados} filas con valores nulos, y {duplicados_eliminados} duplicados") 
        st.session_state.archivo_cargado = True
        
        return df, None, nulos_eliminados, duplicados_eliminados

    except Exception as e:
        return None, f"Error al cargar los datos: {e}", 0, 0


#función para mostrar los gráficos
def mostrar_graficas(df, tipo_grafica):
    st.subheader(f"Visualización: {tipo_grafica}")
    fig, ax = plt.subplots(figsize=(10, 6))

    try:
        col_x = st.session_state.get('chart_x')
        col_y = st.session_state.get('chart_y')

        # Se valida que se haya seleccionado la columna para la equis
        if tipo_grafica != "Gráfico de calor de correlación" and col_x is None:
            st.error("Es necesario eleccionar al menos una columna.")
            return

        # Para este gráfico se requiere que en el dataset por lo menos haya dos columnas numéricas
        if tipo_grafica == "Gráfico de calor de correlación":
            df_corr = df.select_dtypes(include=[np.number]).corr()
            if df_corr.empty or df_corr.shape[0] < 2:
                st.warning("El dataset debe contar con 2 columnas numéricas como mínimo.")
                return 
                
            fig.set_size_inches(12, 10)
            sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
            ax.set_title('Mapa de Calor de Correlación entre Variables Numéricas')

        # Para gráfica de cajas y bigotes
        elif tipo_grafica == "Gráfico de cajas y bigotes":
            sns.boxplot(y=df[col_x], ax=ax)
            ax.set_title(f'Gráfico de Cajas de {col_x}')

        # para gráfica de Pastel
        elif tipo_grafica == "Gráfico de pastel":
            counts = df[col_x].value_counts().head(10)
            if counts.empty:
                st.warning("La columna seleccionada no tiene datos válidos.")
                return
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
            ax.set_title(f'Distribución de {col_x}')
            ax.axis('equal') 
            
        # para gráfica de Dispersión
        elif tipo_grafica == "Gráfico de dispersión":
            if not pd.api.types.is_numeric_dtype(df[col_x]) or (col_y and not pd.api.types.is_numeric_dtype(df[col_y])):
                st.error("El Gráfico de Dispersión requiere que las columnas seleccionadas sean de tipo numéricas.")
                return
            
            sns.scatterplot(x=df[col_x], y=df[col_y] if col_y else None, ax=ax)
            ax.set_title(f'Dispersión: {col_x} vs {col_y if col_y else "Índice"}')

        # Para gráfica de Barras, se definió que sean de dos dimensiones
        elif tipo_grafica == "Gráfico de barras":
            if col_y:
                sns.barplot(x=df[col_x], y=df[col_y], ax=ax)
                ax.set_title(f'Barras: {col_x} por {col_y}')
            else:
                sns.countplot(x=df[col_x], ax=ax)
                ax.set_title(f'Frecuencia de {col_x}')

        # Muestra la gráfica como tal
        st.pyplot(fig)
        plt.close(fig)
            
    except Exception as e:
        st.error(f"No se pudo generar la gráfica: {e}")


# Lógica para manejar la barra lateral donde se carga el archivo
with st.sidebar:
    st.header("⚙️ Cargar Archivo")
    
    archivo_subido = st.file_uploader(
        "Sube un CSV o Excel",
        type=['csv', 'xlsx'],
        key="file_uploader"
    )

    if archivo_subido is not None and not st.session_state.archivo_cargado:
        df_temp, error, nulos_eliminados, duplicados_eliminados = cargar_limpiar_datos(archivo_subido)
        
        if error:
            st.error(error)
            st.session_state.archivo_cargado = False
        elif df_temp is not None:
            st.session_state.df_limpio = df_temp
            st.session_state.nulos_eliminados = nulos_eliminados
            st.session_state.duplicados_eliminados = duplicados_eliminados
            st.rerun()

    elif archivo_subido is None and st.session_state.archivo_cargado:
        
        st.session_state.archivo_cargado = False
        st.session_state.df_limpio = None
        st.session_state.nulos_eliminados = 0 
        st.session_state.duplicados_eliminados = 0
        st.rerun()
        
    if st.session_state.archivo_cargado:
        st.markdown("---")
        st.subheader("🧹 Reporte de Limpieza")
        st.metric(label="Filas con Nulos Eliminadas", value=st.session_state.nulos_eliminados)
        st.metric(label="Filas Duplicadas Eliminadas", value=st.session_state.duplicados_eliminados)

# Manejo de interfaz principal
if st.session_state.archivo_cargado:
    df = st.session_state.df_limpio
    st.subheader("Primeros 5 Registros del Dataset")
    st.dataframe(df.head(), use_container_width=True)
    st.markdown("---")
    
    col_select, col_graph = st.columns([1, 2])

    with col_select:
        opciones_analisis = ["Ver resumen del dataset", "Ver gráfica"]
        analisis_seleccionado = st.selectbox(
            "Selecciona la acción a ejecutar:",
            options=opciones_analisis,
            key='analisis_seleccionado'
        )
        
        if analisis_seleccionado == "Ver gráfica":

            grafica_seleccionada = st.selectbox(
                "Selecciona el tipo de gráfica:",
                options=[
                    "Gráfico de cajas y bigotes",
                    "Gráfico de barras",
                    "Gráfico de pastel",
                    "Gráfico de dispersión",
                    "Gráfico de calor de correlación"
                ],
                key='grafica_seleccionada'
            )
            
            df_cols = df.columns.tolist()
            
            if grafica_seleccionada == "Gráfico de calor de correlación":
                st.info("El Mapa de Calor usa todas las columnas numéricas.")
                st.session_state.chart_x = None 
                st.session_state.chart_y = None 
                
            elif grafica_seleccionada in ["Gráfico de cajas y bigotes", "Gráfico de pastel"]:
                # una Dimensión requerida
                st.selectbox("Columna a analizar (Dimensión 1):", options=[None] + df_cols, key='chart_x')
                st.info(f"Solo se necesita 1 columna para {grafica_seleccionada}.")
                st.session_state.chart_y = None 

            else: # Gráfico de Barras y Dispersión - 2 Dimensiones como máximo
                st.selectbox("Eje X (Dimensión 1):", options=[None] + df_cols, key='chart_x')
                st.selectbox("Eje Y (Dimensión 2 - Opcional):", options=[None] + df_cols, key='chart_y')
                
        if st.button("▶️ Visualizar"):
            st.session_state.accion_solicitada = True


# Visualización de resumen estadístico del dataframe
if st.session_state.archivo_cargado and st.session_state.accion_solicitada:
    df = st.session_state.df_limpio
    
    if st.session_state.analisis_seleccionado == "Ver resumen del dataset":
        st.subheader("Resumen Estadístico del Dataset")
        
        st.write(f"Filas: {df.shape[0]}")
        st.write(f"Columnas: {df.shape[1]}")
        
        st.dataframe(df.describe().T, use_container_width=True)

    elif st.session_state.analisis_seleccionado == "Ver gráfica":
        mostrar_graficas(df, st.session_state.grafica_seleccionada)
    
    st.session_state.accion_solicitada = False 

elif not st.session_state.archivo_cargado:
    st.info("Sube un archivo CSV o Excel en la barra lateral para visualizar los datos.")