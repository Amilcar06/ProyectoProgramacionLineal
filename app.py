# Librerías estándar de Python
import os
import io
import json
import base64

# Librerías para cálculos matemáticos y optimización
import numpy as np
from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, lpSum

# Librerías para visualización y gráficos
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.patches import Polygon

# Librerías para la creación de aplicaciones web
from flask import Flask, render_template, request, session, url_for, send_file

# Librerías para generación de PDFs
from weasyprint import HTML, CSS

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['POST', 'GET'])
def formulario():
    if request.method == 'POST':
        # Recibe los datos iniciales del formulario
        variables_decision = int(request.form.get('decision-variables', 0))
        restricciones = int(request.form.get('constraints', 0))
        tipo_optimizacion = request.form.get('optimizacion', 'maximizacion')
        return render_template(
            'formulario.html',
            variables_decision=variables_decision,
            restricciones=restricciones,
            tipo_optimizacion=tipo_optimizacion
        )
    return "Método no permitido", 405

app.secret_key = 'tu_clave_secreta'

@app.route('/resolver', methods=['POST'])
def resolver():
    # Recibe los datos del formulario
    tipo_optimizacion = request.form.get("tipo_optimizacion", "maximizacion")
    variables_decision = int(request.form.get("variables_decision", 0))
    restricciones = int(request.form.get("restricciones", 0))

    # Coeficientes de la función objetivo
    coeficientes = []
    for i in range(variables_decision):
        try:
            coeficientes.append(float(request.form.get(f"coef_{i}", 0)))
        except ValueError:
            coeficientes.append(0.0)

    # Matriz de restricciones y valores de la derecha
    restricciones_matriz = []
    relaciones = []
    lados_derechos = []

    for j in range(restricciones):
        restriccion = []
        for i in range(variables_decision):
            try:
                restriccion.append(float(request.form.get(f"constraint_{j+1}_var_{i}", 0)))
            except ValueError:
                restriccion.append(0.0)
        restricciones_matriz.append(restriccion)
        relaciones.append(request.form.get(f"constraint_{j+1}_relation", "<"))
        try:
            lados_derechos.append(float(request.form.get(f"constraint_{j+1}_rhs", 0)))
        except ValueError:
            lados_derechos.append(0.0)

    # Crear el problema de optimización
    prob = LpProblem("Problema de Optimización", LpMaximize if tipo_optimizacion == "maximizacion" else LpMinimize)

    # Variables de decisión
    variables = [LpVariable(f"x{i+1}", lowBound=0) for i in range(variables_decision)]

    # Definir la función objetivo
    prob += lpSum([coeficientes[i] * variables[i] for i in range(variables_decision)])

    # Añadir restricciones
    for j in range(restricciones):
        expresion = lpSum([restricciones_matriz[j][i] * variables[i] for i in range(variables_decision)])
        if relaciones[j] == "<":
            prob += expresion <= lados_derechos[j]
        elif relaciones[j] == "=":
            prob += expresion == lados_derechos[j]
        elif relaciones[j] == ">":
            prob += expresion >= lados_derechos[j]

    # Resolver el problema
    prob.solve()

    # Obtener resultados básicos
    resultados = {f"x{i+1}": v.varValue for i, v in enumerate(prob.variables())}
    valor_optimo = prob.objective.value()

    # Cálculos adicionales para análisis de sensibilidad
    costos_reducidos = {v.name: v.dj for v in prob.variables()}  # Costos reducidos

    # Multiplicar por -1 los precios sombra y holguras/superávit
    precios_duales = {f"Restricción {i+1}": c.pi for i, c in enumerate(prob.constraints.values())}  # Precios sombra
    holguras = {f"Restricción {i+1}": c.slack for i, c in enumerate(prob.constraints.values())}  # Holguras/Superávit

    # Gráfica para problemas con 2 variables de decisión
    if variables_decision == 2:
        x = [i for i in range(101)]  # Eje X
        
    # Crear la figura y el eje
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(1, 1, 1)

        # Dibujar restricciones y calcular puntos de intersección
        valores_b = []
        intersecciones = []
        for j in range(restricciones):
            a1, a2 = restricciones_matriz[j][:2]
            b = lados_derechos[j]
            valores_b.append(b)
            if a2 != 0:  # Restricción no vertical
                y_vals = [(b - a1 * xi) / a2 for xi in x]
                ax.plot(x, y_vals, label=f"Restricción {j+1}", linewidth=1.5)
                # Guardar extremos de las líneas
                intersecciones.append((0, b / a2))  # Cuando x1 = 0
                intersecciones.append((100, (b - 100 * a1) / a2))  # Cuando x1 = 100
            else:  # Restricción vertical
                x_intercept = b / a1
                ax.axvline(x=x_intercept, color='red', linestyle='--', label=f"Restricción {j+1}")
                intersecciones.append((x_intercept, 0))
                intersecciones.append((x_intercept, 100))

        restricciones_matriz = [restriccion + [b] for restriccion, b in zip(restricciones_matriz, valores_b)]
        print("Restricciones:", restricciones_matriz)
        for restriccion in restricciones_matriz:
            if len(restriccion) != 3:
                raise ValueError(f"Restricción inválida: {restriccion}. Se esperaban 3 valores (a1, a2, b).")
        # Encontrar puntos factibles (intersecciones válidas)
        puntos_factibles = []
        for x1, y1 in intersecciones:
            if x1 is not None and y1 is not None:  # Verificar que x1, y1 son válidos
                if all(a1 * x1 + a2 * y1 <= b for a1, a2, b in restricciones_matriz):
                    puntos_factibles.append((x1, y1))


        # Ordenar los puntos para formar un polígono
        if puntos_factibles:
            puntos_factibles = sorted(puntos_factibles, key=lambda p: (p[0], p[1]))
            poligono = Polygon(puntos_factibles, closed=True, color='lightblue', alpha=0.4, label="Región factible")
            ax.add_patch(poligono)

        # Dibujar solución óptima
        ax.scatter(resultados["x1"], resultados["x2"], color='green', label='Solución óptima', s=100, zorder=5)

        # Ajustar límites de los ejes
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        # Añadir líneas de cuadrícula
        ax.grid(True, linestyle='--', alpha=0.6)

        # Configurar el diseño
        ax.set_title("Espacio factible y solución óptima", fontsize=14, fontweight='bold')
        ax.set_xlabel("x1", fontsize=12)
        ax.set_ylabel("x2", fontsize=12)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.legend(fontsize=10)

        # Guardar la figura en formato PNG
        output = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(output)

        # Generar un nombre único para la imagen
        import uuid
        image_name = f"graph_{uuid.uuid4().hex}.png"

        # Guardar la imagen en una carpeta temporal
        image_path = f"static/images/{image_name}"
        with open(image_path, 'wb') as f:
            f.write(output.getvalue())
        # Guarda solo la ruta en la sesión
        session['graph_url'] = image_path

        # Almacenar datos en la sesión como cadenas JSON
        session['resultados'] = json.dumps(resultados)
        session['valor_optimo'] = valor_optimo
        session['tipo_optimizacion'] = tipo_optimizacion
        session['reduced_costs'] = json.dumps(costos_reducidos)
        session['shadow_prices'] = json.dumps(precios_duales)
        session['slack_surplus'] = json.dumps(holguras)

        # Renderizar el HTML con la gráfica
        return render_template(
            'resultado.html',
            resultados=resultados,
            valor_optimo=valor_optimo,
            tipo_optimizacion=tipo_optimizacion,
            reduced_costs=costos_reducidos,
            shadow_prices=precios_duales,
            slack_surplus=holguras,
            graph_url=image_path
        )
    else:
        # Renderizar resultados sin gráfica
        return render_template(
            'resultado.html',
            resultados=resultados,
            valor_optimo=valor_optimo,
            tipo_optimizacion=tipo_optimizacion,
            reduced_costs=costos_reducidos,
            shadow_prices=precios_duales,
            slack_surplus=holguras
        )
    
@app.route('/download_pdf')
def download_pdf():
    # Recuperar los resultados de la sesión
    resultados = json.loads(session.get('resultados', '{}'))
    valor_optimo = session.get('valor_optimo', 0)
    tipo_optimizacion = session.get('tipo_optimizacion', 'maximizacion')
    reduced_costs = json.loads(session.get('reduced_costs', '{}'))
    shadow_prices = json.loads(session.get('shadow_prices', '{}'))
    slack_surplus = json.loads(session.get('slack_surplus', '{}'))
    image_path = session.get('graph_url', '')

    # Convertir image_path a una URL completa
    if image_path:
        graph_url = url_for('static', filename=image_path.split('static/')[-1], _external=True)
    else:
        graph_url = ''
    # Renderizar el HTML que deseas convertir a PDF
    rendered = render_template('impresion.html', 
                               resultados=resultados,
                               valor_optimo=valor_optimo,
                               tipo_optimizacion=tipo_optimizacion,
                               reduced_costs=reduced_costs,
                               shadow_prices=shadow_prices,
                               slack_surplus=slack_surplus,
                               graph_url=graph_url
    )

    # Ruta a la hoja de estilos
    css_path = os.path.join(app.static_folder, 'css/impresion.css')

    # Generar PDF con WeasyPrint
    pdf = HTML(string=rendered).write_pdf(stylesheets=[CSS(css_path)])

    # Enviar el PDF como archivo para descargar
    return send_file(
        io.BytesIO(pdf), 
        as_attachment=True, 
        download_name='resultados.pdf', 
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
    