from flask import Flask, render_template, request, redirect, url_for, flash, session
import xml.etree.ElementTree as ET
import pandas as pd
import controladores.semestre as sem
import controladores.docentes as doc
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('docente/insertar_docente.html')

#semestres

# @app.route('/semestres')
# def listarSemestre():
#     semestre = sem.listar()
#     return render_template('semestres/listarSemestre.html', semestre = semestre)

# @app.route('/editar_semestre/<int:id>')
# def editarSemestre(id):
#     semestre = sem.buscarSemestre(id)
#     return render_template('semestres/editarSemestre.html', semestre = semestre)

# @app.route('/eliminar_semestre/<int:id>')
# def eliminarSemestre(id):
#     sem.eliminarSemestre(id)
#     return redirect(url_for('listarSemestre'))

# @app.route('/actualizar_semestre', methods=['POST'])
# def actualizarSemestre():
#     id = request.form['id']
#     nombre = request.form['nombre']
#     fecha_inicio = request.form['fecha_inicio']
#     fecha_fin = request.form['fecha_fin']
#     vigencia = request.form['vigencia']
#     sem.editarSemestre(id, nombre, fecha_inicio, fecha_fin, vigencia)
#     return redirect(url_for('listarSemestre'))

# #docentes

# @app.route('/docentes')
# def listarDocente():
#     docente = doc.listar()
#     return render_template('docentes/listar_docente.html', docente = docente)

# @app.route('/insertarDocente', methods=['POST'])
# def insertarDocente():
#     semestre_id = request.form['semestre_id']
#     nombre = request.form['nombre']
#     apellido = request.form['apellido']
#     correo = request.form['correo']
#     dedicacion = request.form['dedicacion']
#     telefono = request.form['telefono']
#     hora_asesoria = request.form['hora_asesoria']
#     doc.insertarDocente(semestre_id,nombre, apellido, correo, dedicacion,telefono, hora_asesoria)
#     return redirect(url_for('listarDocente'))


docentes = []

def find_start_row(df, columns):
    """Encuentra la fila inicial donde todas las columnas especificadas están presentes, considerando múltiples posibles nombres."""
    for index, row in df.iterrows():
        if all(any(col.lower() in str(x).lower() for x in row.values) for col in columns):
            return index
    return None


@app.route('/insertar', methods=['GET', 'POST'])
def upload_and_display():
    global docentes  
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if file.filename.endswith(('.xml', '.xlsx', '.csv')):
                if file.filename.endswith('.xml'):
                    tree = ET.parse(file)
                    root = tree.getroot()
                    for docente in root.findall('.//docente'):
                        data = {}
                        fields = ['semestre', 'nombre', 'apellido', 'correo', 'dedicacion', 'telefono']
                        for field in fields:
                            element = docente.find(field)
                            if element is not None:
                                data[field] = element.text
                            else:
                                data[field] = 'No especificado'
                        docentes.append(data)
                
                elif file.filename.endswith(('.xlsx', '.csv')):
                    if file.filename.endswith('.xlsx'):
                        df = pd.read_excel(file, header=None)
                    else:
                        df = pd.read_csv(file, header=None)
                    
                    expected_columns = ['semestre', 'nombre', 'apellido', 'correo', 'dedicacion', 'telefono']
                    start_row = find_start_row(df, expected_columns)
                    if start_row is not None:
                        df.columns = df.iloc[start_row].apply(lambda x: x.lower() if isinstance(x, str) else x)
                        df = df[start_row+1:]
                        df = df.loc[:, df.columns.isin(expected_columns)].copy()  # Filtramos solo las columnas esperadas
                        docentes = df.to_dict(orient='records')
                    else:
                        missing_columns = [col for col in expected_columns if col not in df.columns]
                        return f"Error: Faltan las siguientes columnas en el archivo: {', '.join(missing_columns)}"
                                         
    return render_template('docente/insertar_docente.html', docentes=docentes)

@app.route('/update_docente', methods=['POST'])
def update_docente():
    index = int(request.form['index'])
    docentes[index]['nombre'] = request.form['nombre']
    docentes[index]['apellido'] = request.form['apellido']
    docentes[index]['correo'] = request.form['correo']
    docentes[index]['dedicacion'] = request.form['dedicacion']
    docentes[index]['telefono'] = request.form['telefono']
    return redirect(url_for('upload_and_display'))

# insertar docente en la base de datos desde la tabla


@app.route('/insertar_docentes', methods=['POST'])
def insertar_docentes():
    nombres = request.form.getlist('nombre[]')
    apellidos = request.form.getlist('apellido[]')
    correos = request.form.getlist('correo[]')
    dedicaciones = request.form.getlist('dedicacion[]')
    telefonos = request.form.getlist('telefono[]')
    
    for i in range(len(nombres)):
        doc.insertarDocente(nombres[i], apellidos[i], correos[i], dedicaciones[i], telefonos[i])
    
    return redirect(url_for('upload_and_display'))  




if __name__ == '__main__':
    app.run( debug=True)
