"""from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['POST', 'GET'])
def formulario():
    if request.method == 'POST':
        variables_decision = int(request.form.get('decision-variables', 0))
        restricciones = int(request.form.get('constraints', 0))
        tipo_optimizacion = request.form.get('optimizacion', 'maximizacion')
        #print(decision_variables, constraints, optimization_type)
        return render_template('formulario.html', variables_decision=variables_decision, restricciones=restricciones, tipo_optimizacion=tipo_optimizacion)
    return "Método no permitido", 405

if __name__ == '__main__':
    app.run(debug=True)
"""

from flask import Flask, render_template, request
from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, lpSum

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

@app.route('/resolver', methods=['POST'])
def resolver():
    # Recibe los datos del formulario
    tipo_optimizacion = request.form.get("tipo_optimizacion", "maximizacion")
    variables_decision = int(request.form.get("variables_decision", 0))
    restricciones = int(request.form.get("restricciones", 0))

    # Coeficientes de la función objetivo
    coeficientes = [float(request.form.get(f"coef_{i}", 0)) for i in range(variables_decision)]
    # Matriz de restricciones y valores de la derecha
    restricciones_matriz = []
    relaciones = []
    lados_derechos = []

    for j in range(restricciones):
        restriccion = [float(request.form.get(f"constraint_{j+1}_var_{i}", 0)) for i in range(variables_decision)]
        restricciones_matriz.append(restriccion)
        relaciones.append(request.form.get(f"constraint_{j+1}_relation", "<"))
        lados_derechos.append(float(request.form.get(f"constraint_{j+1}_rhs", 0)))

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

    # Obtener resultados
    resultados = {v.name: v.varValue for v in prob.variables()}
    valor_optimo = prob.objective.value()

    # Renderizar los resultados
    return render_template(
        'resultado.html',
        resultados=resultados,
        valor_optimo=valor_optimo,
        tipo_optimizacion=tipo_optimizacion
    )

if __name__ == '__main__':
    app.run(debug=True)
