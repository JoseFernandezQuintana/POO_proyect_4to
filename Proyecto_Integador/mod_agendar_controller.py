import re
from typing import List, Dict, Any
from difflib import SequenceMatcher
from typing import List, Dict, Any, Union

# --- Base de datos de ejemplo (Simulación) ---
# Usualmente esto interactuaría con una base de datos real (SQL, MongoDB, etc.)
DB_CITAS = [
    {
        'id': 101, 'nombre_completo': 'Juan Pérez López', 'telefono': '8715551234', 
        'doctora': 'Dra. Raquel Guzmán Reyes (Ortodoncia)', 'tratamiento': 'Ajuste de Brackets',
        'fecha_cita': '2025-12-01', 'hora_cita': '10:00', 'costo_sesion': '800.00', 'nota': 'Ligas azules.'
    },
    {
        'id': 102, 'nombre_completo': 'María Fernanda Gónzalez', 'telefono': '3331234567', 
        'doctora': 'Dra. Paola Jazmin Vera Guzmán (Endodoncia)', 'tratamiento': 'Endodoncia de molar',
        'fecha_cita': '2025-12-02', 'hora_cita': '14:30', 'costo_sesion': '2500.00', 'nota': 'Primera fase.'
    },
    {
        'id': 103, 'nombre_completo': 'Luis Alberto Sánchez', 'telefono': '5559876543', 
        'doctora': 'Dra. Raquel Guzmán Reyes (Ortodoncia)', 'tratamiento': 'Presupuesto Inicial',
        'fecha_cita': '2025-12-03', 'hora_cita': '09:00', 'costo_sesion': '0.00', 'nota': ''
    },
]

class ModificarCitaController:
    def __init__(self):
        self.citas_data = DB_CITAS

    def _match_score(self, a: str, b: str) -> float:
        """Calcula una puntuación de similitud entre dos cadenas (0.0 a 1.0)."""
        # Se convierte a minúsculas y se eliminan espacios para la comparación flexible
        a = a.lower().replace(' ', '')
        b = b.lower().replace(' ', '')
        return SequenceMatcher(None, a, b).ratio()

    def buscar_citas_flexibles(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca citas basándose en una consulta, permitiendo errores de tipografía
        y nombres/teléfonos parciales, con una lógica de 'coincidencia flexible'.
        """
        if len(query) < 3:
            return []
        
        query = query.strip().lower()
        resultados_filtrados = []
        
        for cita in self.citas_data:
            nombre = cita['nombre_completo'].lower()
            telefono = cita['telefono'].lower()
            
            score_nombre = 0.0
            score_telefono = 0.0

            # 1. Búsqueda por Subcadena (para nombres/teléfonos parciales)
            if query in nombre:
                score_nombre = 1.0 # Coincidencia exacta de subcadena
            
            # Buscamos el query sin formato en el teléfono
            if re.sub(r'[^0-9]', '', query) in re.sub(r'[^0-9]', '', telefono):
                score_telefono = 1.0 # Coincidencia exacta de subcadena en número

            # 2. Búsqueda por Similitud (para errores tipográficos o falta de nombre completo)
            if score_nombre < 1.0: # Solo si no hubo una coincidencia de subcadena perfecta
                 # Comparamos la cadena de consulta con el nombre completo y cada palabra del nombre
                 score_nombre = max([self._match_score(query, nombre), 
                                     *[self._match_score(query, part) for part in nombre.split()]])

            # Tomamos la mejor puntuación entre nombre y teléfono
            final_score = max(score_nombre, score_telefono)
            
            # Umbral de Coincidencia: Solo incluimos resultados con un score alto
            if final_score >= 0.7: # Umbral de 70% de similitud o subcadena
                cita_info = {
                    'display': f"ID {cita['id']} | {cita['nombre_completo']} | {cita['fecha_cita']} {cita['hora_cita']}",
                    'id': cita['id'],
                    'score': final_score # Para ordenar los resultados
                }
                resultados_filtrados.append(cita_info)

        # Ordenar por el score más alto (mejor coincidencia)
        resultados_filtrados.sort(key=lambda x: x['score'], reverse=True)
        
        return resultados_filtrados

    def obtener_datos_cita(self, cita_id: int) -> Union[Dict[str, Any], None]:
        """Obtiene todos los datos de una cita específica por su ID."""
        return next((cita for cita in self.citas_data if cita['id'] == cita_id), None)
        
    def obtener_doctoras(self):
        """Método para obtener la lista de doctoras (reutilizado de agendar_view)"""
        return sorted(list(set([d['doctora'] for d in self.citas_data])))