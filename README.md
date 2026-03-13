# ⚽ MMJ World Cup Simulator

Simulador completo de Copa del Mundo con clasificatorias por confederación.

## 📁 Estructura
```
world_cup_app/
├── app.py          # Aplicación principal Streamlit
├── data.py         # Base de datos: equipos, jugadores, rankings
├── state.py        # Lógica de simulación y gestión de estado
├── requirements.txt
└── README.md
```

## 🚀 Deploy en Streamlit Cloud

1. Sube los archivos a un repositorio de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. Configura:
   - **Main file path:** `app.py`
   - **Python version:** 3.10+
5. ¡Deploy!

## 🏆 Flujo del Simulador

### 1. Copas de Confederación
- **Eurocopa (UEFA):** 24 equipos → bracket completo
- **Copa América (CONMEBOL):** 10 equipos → 2 grupos + bracket
- **Copa África (CAF):** 10 equipos → 2 grupos + bracket
- **Copa Oro (CONCACAF):** 6 equipos → 2 grupos + bracket
- **Copa Asia (AFC):** 6 equipos (Australia incluida) → bracket

### 2. Eliminatorias por Confederación
- **UEFA:** Puestos 6-21 → 4 grupos → top 2 c/u = 8 clasificados
- **CONMEBOL:** Puestos 2-7 → todos vs todos → top 3 + 4to a repechaje
- **CAF:** Puestos 3-7 → todos vs todos → top 3
- **CONCACAF:** Puestos 2-5 → todos vs todos → top 2 + 3ro a repechaje
- **AFC:** Puestos 2-5 → todos vs todos → top 3 + 4to a repechaje

### 3. Repechaje Internacional
- CONCACAF 3ro vs AFC 4to
- CONMEBOL 4to vs Nueva Zelanda

### 4. Mundial
- 32 equipos · 8 grupos · Eliminación directa
- Host elegido manualmente

### 5. Ranking FIFA
- Se actualiza automáticamente con cada torneo
- Persiste entre temporadas
- Se resetea solo manualmente

## ⚽ Cupos Totales
| Confederación | Directos | Playoffs | Repechaje | Total |
|---|---|---|---|---|
| UEFA | 5 | 8 | 0 | 13 |
| CONMEBOL | 1 | 3 | 1 | 4 |
| CAF | 2 | 3 | 0 | 5 |
| CONCACAF | 1 | 2 | 1 | 3 |
| AFC | 1 | 3 | 1 | 4 |
| Repechaje Int | 0 | 0 | 2 | 2 |
| Host | 1 | 0 | 0 | 1 |
| **TOTAL** | | | | **32** |
