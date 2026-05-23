# Barómetro Digital 2026

**Análisis de conversación pública sobre la segunda vuelta presidencial del Perú**

🔗 [Ver dashboard en vivo](https://emily-mm.github.io/barometro-elecciones-2026/)

---

## ¿Qué es?

El Barómetro Digital 2026 es un proyecto de análisis político que trackea en tiempo real cómo se habla de los dos candidatos a la presidencia del Perú en plataformas digitales abiertas.

Cada día, de forma automática, el sistema recolecta comentarios, búsquedas y menciones sobre **Keiko Fujimori** (Fuerza Popular) y **Roberto Sánchez** (Juntos por el Perú), y los convierte en visualizaciones que permiten seguir la evolución del debate público.

---

## ¿Qué mide?

**Menciones** — cuánto se habla de cada candidato en YouTube, Reddit y TikTok cada día.

**Sentimiento** — si la conversación es positiva, neutral o negativa, usando un modelo de inteligencia artificial entrenado en español latinoamericano ([robertuito](https://huggingface.co/pysentimiento/robertuito-sentiment-analysis)).

**Google Trends** — el interés de búsqueda en Google de los últimos 30 días, como indicador de atención pública.

**Top búsquedas** — qué términos asocian los peruanos a cada candidato al buscar en Google.

---

## Fuentes de datos

| Plataforma | Método | Frecuencia |
|---|---|---|
| YouTube | Comentarios via YouTube Data API v3 | Automático, 2x/día |
| Reddit | Posts y comentarios de r/peru y r/ATMP | Automático, 2x/día |
| Google Trends | Serie de tiempo de búsquedas | Automático, 2x/día |
| TikTok | Capturas manuales con Zeeschuimer | Fechas clave |

---

## Fechas clave

- **31 de mayo** — Debate presidencial
- **7 de junio** — Segunda vuelta

---

## Metodología

- Los textos se recolectan de plataformas públicas sin autenticación de usuarios.
- El análisis de sentimiento se corre localmente con `pysentimiento/robertuito`, un modelo transformer entrenado en tweets en español.
- Se analizan hasta 200 textos por candidato por fuente para mantener tiempos de procesamiento razonables.
- Los datos se actualizan automáticamente dos veces al día via GitHub Actions y se publican como archivos JSON en este repositorio.
- Este proyecto es de carácter informativo y no tiene afiliación política con ningún candidato ni partido.

---

## Stack técnico

Python · YouTube Data API · Reddit JSON API · pytrends · pysentimiento · GitHub Actions · Chart.js · GitHub Pages

---

*Proyecto personal · Lima, Perú · 2026*
