# **Sistema Interactivo para Resolución de Programación Lineal con Método Simplex**

**Sistema Interactivo para Resolución de Programación Lineal con Método Simplex: Implementación del Método Simplex para Maximización y Minimización**

Este proyecto es una aplicación basada en Python y Flask que permite resolver problemas de programación lineal utilizando el método Simplex. Está diseñado para facilitar la resolución de modelos matemáticos de optimización, tanto en problemas de maximización como de minimización.

## **Características Principales**
- Interfaz intuitiva para ingresar las variables de decisión, coeficientes y restricciones del modelo.
- Soporte para seleccionar el tipo de optimización (Maximización o Minimización).
- Implementación eficiente del método Simplex para obtener resultados precisos.
- Salida detallada del proceso de cálculo y la solución óptima.
- Diseño responsivo y accesible para diferentes tamaños de pantalla.

## **Objetivo del Proyecto**
El objetivo principal de este proyecto es ofrecer una herramienta práctica y educativa para estudiantes y profesionales interesados en aprender y aplicar el método Simplex en la resolución de problemas reales de programación lineal. 

Este sistema simplifica la formulación y solución de modelos matemáticos al proporcionar un entorno amigable para realizar cálculos complejos con facilidad.

## Requisitos Previos

- Python 3.8 o superior.
- Flask 2.x.
- Paquete `pulp` para optimización.

## Instalación

1. Clona el repositorio en tu máquina local:
   ```bash
   git clone https://github.com/Amilcar06/ProyectoProgramacionLineal.git
   ```

2. Navega al directorio del proyecto:
   ```bash
   cd ProyectoProgramacionLineal
   ```

3. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

4. Instala las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```

5. Ejecuta la aplicación:
   ```bash
   flask run
   ```

6. Accede a la aplicación desde tu navegador en `http://127.0.0.1:5000`.

## Uso

1. Ingresa el número de variables de decisión y restricciones, y selecciona el tipo de optimización (maximización o minimización).
2. Proporciona los coeficientes de la función objetivo y las restricciones en los formularios generados.
3. Visualiza los resultados en la página de resultados, incluyendo:
   - Valores óptimos de las variables de decisión.
   - Valor de la función objetivo.
   - Análisis de sensibilidad.

## Estructura del Proyecto

```
/ProyectoProgramacionLineal
├── app.py             # Archivo principal de la aplicación Flask.
├── templates/         # Plantillas HTML (index.html, formulario.html, resultado.html).
├── static/            # Archivos estáticos como CSS, JS, e imágenes.
├── requirements.txt   # Lista de dependencias del proyecto.
├── README.md          # Documentación del proyecto.
```

## Autor

- **Nombre:** Amilcar Josias Yujra Chipana
- **Email:** amilcaryujra23@gmail.com
- **GitHub:** [Amilcar Yujra](https://github.com/Amilcar06)

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.
