Aplicación para visualización de datos de un dataset (Streamlit App)
Este proyecto es una aplicación web interactiva creada con Streamlit de Python que permite a los usuarios cargar datos 
en formato CSV o Excel y a partir de ello poder visualizar el detalle de la información y gráficas.

Funcionalidades Principales:

Carga de archivos CSV mediante la interfaz de usuario.
Visualización de de datos nullos y duplicados eliminados
Visualización de detalles del dataset.
Visualización de gráficas de los datos



Ejecución del programa:
Para ejecutar esta aplicación localmente, necesitas tener Python y las siguientes librerías instaladas.

*streamlit
*pandas
*matplotlib
*seaborn
*numpy


Este comando permite lanzar la aplicación
streamlit run app.py

O se puede intentar también de esta manera
python –m streamlit run app.py

En caso de que se requiera instalar streamlit, se puede hacer de esta forma:
pip install streamlit


La aplicación una vez lanzada se visualizará en el navegador por medio de esta url
http://localhost:8501/.

Se incluye el dataset en formato CSV con el que se validó el funcionamiento, para poder cargarlo
es necesario usar la el botón "Cargar Arcchivo" de la barra lateral izquierda.


Autor: Luciano May