import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "Proyecto Final ANM 2024-2.xlsx"  # Asegúrate de que esta ruta sea correcta

# Paso 3: Leer el archivo Excel
excel_data = pd.ExcelFile(file_path)

# Cargar la hoja de interés
sheet_name = 'cumulative-number-of-notable-ai'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Extraer las columnas de "Year" y "Games" y limpiarlas
games_data = df[['Games', 'Unnamed: 3']].copy()
games_data.columns = ['Year', 'Games']

# Convertir los años y los datos de 'Games' a valores numéricos
games_data = games_data[games_data['Year'] != 'Year']  # Eliminar filas no deseadas
games_data['Year'] = pd.to_numeric(games_data['Year'], errors='coerce')
games_data['Games'] = pd.to_numeric(games_data['Games'], errors='coerce')

# Filtrar datos no nulos
games_data_clean = games_data.dropna()

# Extraer los datos limpios
years = games_data_clean['Year'].values
games_values = games_data_clean['Games'].values


# Función para calcular los coeficientes de los splines cúbicos
def calcular_splines_cubicos(x, y):
    n = len(x) - 1  # Número de intervalos
    h = np.diff(x)  # Diferencias entre los años (pasos)

    # Crear la matriz y el vector de soluciones
    A = np.zeros((n + 1, n + 1))
    b = np.zeros(n + 1)

    # Ecuaciones internas (continuidad de la segunda derivada)
    for i in range(1, n):
        A[i, i - 1] = h[i - 1]
        A[i, i] = 2 * (h[i - 1] + h[i])
        A[i, i + 1] = h[i]
        b[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

    # Condiciones de frontera: spline natural (segunda derivada igual a 0 en los extremos)
    A[0, 0] = 1
    A[n, n] = 1

    # Resolver para los coeficientes c
    c = np.linalg.solve(A, b)

    # Calcular coeficientes a, b, d
    a = y[:-1]
    b = (y[1:] - y[:-1]) / h - h * (2 * c[:-1] + c[1:]) / 3
    d = (c[1:] - c[:-1]) / (3 * h)

    return a, b, c[:-1], d  # c[:-1] ya que el último valor de c no se usa


# Calcular los coeficientes para los splines cúbicos
a, b, c, d = calcular_splines_cubicos(years, games_values)


# Función para evaluar el spline cúbico en un punto
def evaluar_spline(a, b, c, d, x, x_points):
    for i in range(len(x_points) - 1):
        if x_points[i] <= x <= x_points[i + 1]:
            dx = x - x_points[i]
            return a[i] + b[i] * dx + c[i] * dx ** 2 + d[i] * dx ** 3
    return None


# Generar nuevos puntos para la interpolación
new_years = np.arange(years.min(), years.max(), 0.1)
interpolated_values = [evaluar_spline(a, b, c, d, x, years) for x in new_years]

# Graficar los datos originales y los interpolados con splines cúbicos manuales
plt.figure(figsize=(10, 6))
plt.plot(years, games_values, 'o', label='Datos originales (Games)', markersize=6)
plt.plot(new_years, interpolated_values, '-', label='Interpolación con Splines Cúbicos (Manual)', lw=2)
plt.xlabel('Años')
plt.ylabel('Número de sistemas IA (Games)')
plt.title('Interpolación de IA en Videojuegos (Splines Cúbicos Manual)')
plt.legend()
plt.grid(True)
plt.show()

# Filtrar los años que faltan
years_set = set(years)  # Conjunto de años originales
faltantes = {}

# Obtener solo un valor para cada año que falta
for year, value in zip(new_years, interpolated_values):
    año_redondeado = int(round(year))
    if año_redondeado not in years_set and año_redondeado not in faltantes:
        faltantes[año_redondeado] = value

# Crear un DataFrame para mostrar los años faltantes e interpolados
resultados_faltantes = pd.DataFrame(list(faltantes.items()), columns=['Año', 'Games Interpolados'])

# Imprimir los resultados faltantes
print(resultados_faltantes)
