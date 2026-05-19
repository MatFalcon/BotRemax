# BotRemax (remax_2)

Bot de automatización inmobiliaria. Scrapea propiedades de **Century21 Paraguay** y las republica en **Clasipar** e **InfoCasas**. Pese al nombre `RemaxScrap`, la fuente actual es Century21.

Todo el código vive en `remax_2/`. Entry point: [remax_2/ejecucion_bot.py](remax_2/ejecucion_bot.py).

---

## Arquitectura y flujo de `ejecucion_bot.py`

### Módulos implicados

| Archivo | Rol |
|---|---|
| [ejecucion_bot.py](remax_2/ejecucion_bot.py) | Orquestador. Lee configuración, dispara scrapeo y publicación, controla el navegador Edge. |
| [scrapeador_century.py](remax_2/scrapeador_century.py) | Clase `RemaxScrap` y `BaseCentury`. Scraping de Century21 y gestión del CSV. |
| [publicar_clasipar.py](remax_2/publicar_clasipar.py) | Publicación automatizada en Clasipar (entry: `procesar_clasipar`). |
| [publicar_info.py](remax_2/publicar_info.py) | Publicación en InfoCasas (entry: `iniciar_sesion_infocasas` + `recorrer_resultados_pendientes_a_publicar_info`). |
| [publicar_hendyla.py](remax_2/publicar_hendyla.py) | Publicación en Hendyla — **bloque comentado, no se ejecuta**. |
| [credenciales.py](remax_2/credenciales.py) | Lee `driver/Pass.xlsx` (usuarios por portal, ciudad a scrapear). |
| [variables.py](remax_2/variables.py) | XPaths, URLs, rutas, mapa de categorías para mapeo de tipos. |
| [navegador_scrap.py](remax_2/navegador_scrap.py) | Clase `Navegador`, wrapper de Selenium con esperas y helpers. |
| [para_log.py](remax_2/para_log.py) | Escritura de `log.txt`. **Abre con `encoding="utf-8"`** — sin eso fallaba al loggear `→`/`²`. |
| `driver/Pass.xlsx` | Configuración. Hojas: 0=InfoCasas, 1=Hendy, 2=Clasi, 3=Configuración. Hoja 3 celda A8 = ciudad. Columna B filas 2-4 = cantidades. |
| `driver/remax_propiedades.csv` | Base de propiedades. Estado del bot. |
| `driver/msedgedriver.exe` | WebDriver para Microsoft Edge. |

### Flujo de ejecución

```
ejecucion_bot.py
  ├─ variables_configuracion()      # lee cantidades del Excel
  ├─ realizar_validacion_duplicados_base()  # limpia ides repetidos del CSV
  ├─ obtener_ciudad_scrapear()      # ciudad desde Excel A8
  ├─ ejecutar_por_ciudad(ciudad)
  │    ├─ RemaxScrap.instanciar_navegador()
  │    ├─ RemaxScrap.abrir_navegador()
  │    ├─ RemaxScrap.abrir_base()
  │    ├─ [si cantidad_agregar > 0]
  │    │    ├─ buscar_ciudad()
  │    │    └─ recorrer_ventanas()         # solo guarda LINK (no abre detalle)
  │    └─ [si cantidad_scrapear > 0]
  │         └─ scrapear_propiedades_pendientes()
  │              └─ por cada link sin titulo:
  │                   abrir_url → extraer_titulo → extraer_tipo_propiedad
  │                   → extraer_precio → extraer_id → extraer_descripcion
  │                   → extraer_ano_construccion → extraer_metros
  │                   → extraer_atributos_tabla → descargar_imagenes
  └─ [si cantidad_publicar > 0]
       realizar_publicaciones()
         ├─ validar_columna_usuario(creds_info / creds_clasi)
         ├─ marcar_precios_invalidos_como_publicado()   # marca '1' silencioso
         ├─ POR USUARIO de Clasipar con ingresa="Si":
         │    pp.procesar_clasipar(driver, usuario, creds, cantidad_publicar)
         └─ POR USUARIO de InfoCasas con ingresa="Si":
              pi.iniciar_sesion_infocasas(...)
              pi.recorrer_resultados_pendientes_a_publicar_info(...)
```

### Tres parámetros de configuración (Excel hoja 4, columna B)

| Variable | Celda | Significado |
|---|---|---|
| `cantidad_propiedades` (scrapear) | B2 | Cuántas propiedades pendientes extraer datos completos. |
| `cantidad_publicar` | B3 | Cuántas publicar **por usuario** en cada portal. |
| `cantidad_agregar` | B4 | Cuántos links nuevos guardar al recorrer las páginas. |

### Decisiones de diseño actuales

- **Agregar** solo guarda link, ciudad y fecha. El `tipo` ya **no** se extrae abriendo cada detalle (era costoso); se completa después en el scrapeo. Las filas recién agregadas quedan con `tipo = "Sin Tipo"`.
- **Atributos del bloque principal** (Terreno, Construcción, Año, etc.) se extraen iterando los `div` hijos y matcheando por nombre del label, **no por posición**. La función clave es `_atributos_bloque_principal()` que devuelve dict `{label_normalizado: valor}`.
- **Validación de precio** corre una sola vez al inicio de `realizar_publicaciones()`. Marca silenciosamente `'1'` en `{N}publicado_info` y `{N}publicado_clasipar` para filas con precio inválido (NaN, sin moneda, no numérico) — evita gastar intentos en datos rotos.
- **Marca de "Eliminado"**: si la página no carga o devuelve 404, el scrapeador escribe `"Eliminado"` en `titulo` y `descripcion`, y `1` en todas las columnas `*publicado*`. **La fila queda fuera de scrapeo y publicación permanentemente** — es destructivo, ojo si el sitio está caído temporalmente.

---

## Esquema del CSV (`driver/remax_propiedades.csv`)

### Columnas fijas

| Columna | Tipo | Origen | Notas |
|---|---|---|---|
| `link` | str | URL completa de la propiedad en Century21. | Clave única lógica. |
| `tipo` | str | Categoría (`casa`, `departamento`, `terreno`, `casa-duplex`, etc.) | Se mapea a IDs de portales en `variables.categorias`. |
| `precio` | str | Formato `"NUMERO MONEDA"` — ej. `"1155428495 GS"`, `"85000 $"`. | Si está mal formateado, la validación inicial marca la fila como publicada. |
| `descripcion` | str | Texto completo de la descripción. | `"Eliminado"` si la página no carga. |
| `titulo` | str | Título de la propiedad. | `"Eliminado"` si la página no carga. Es la "llave de pendiente": filas con título vacío son candidatas a scrapear. |
| `banio` | int | Cantidad de baños. | Extraído de `extraer_atributos_tabla`. |
| `habitaciones` | int | Cantidad de dormitorios. | Idem. |
| `ide` | float | ID interno de Century21 (extraído del texto "ID: 48710"). | El usuario lo ve como número entero. |
| `fecha_inserion` | str | `dd/mm/yyyy` local cuando se agregó el link. | No es la fecha del scrapeo. |
| `ciudad` | str | Clave de ciudad (`Asuncion`, `Lamba`, `Luque`, etc., mapeada en `RemaxScrap.ciudad_campo`). | Viene del Excel hoja 4 A8. |
| `agente_remax` | str | Histórico, no se usa con Century21. | |
| `mts` | int | Metros de terreno. | Extraído de `extraer_metros` (bloque Terreno/Construcción). |
| `mts_construccion` | int | Metros construidos. | Idem. |
| `ano_construccion` | str | Año de construcción. | Extraído por `extraer_ano_construccion`, busca por label "Año de Construcción" en el bloque principal. |
| `intentos` | int | Contador genérico (heredado, prácticamente sin uso actual). | Default `1`. |
| `intentos_info` | int | Intentos fallidos de publicación en InfoCasas. | Filtro `< 3` corta el reintento. |
| `intentos_clasi` | int | Intentos fallidos de publicación en Clasipar. | Filtro `< 4` corta el reintento. |

### Columnas genéricas heredadas (no se usan activamente)

`publicado_clasipar`, `publicado_info`, `publicado_facebook`, `publicado_hendyla` — sin prefijo de usuario. Vienen del modelo en `crear_nueva_fila` pero ya no se leen para filtrar.

### Columnas dinámicas por usuario

Para cada `numero_usuario` definido en el Excel se crean columnas (vía `validar_columna_usuario` en [ejecucion_bot.py:117](remax_2/ejecucion_bot.py#L117)):

| Patrón | Significado | Valor |
|---|---|---|
| `{N}publicado_info` | Estado de publicación del usuario `N` en InfoCasas. | `NaN` = pendiente, `'1'` = publicada/excluida. |
| `{N}publicado_clasipar` | Idem para Clasipar. | Idem. |
| `{N}publicado_hendyla` | Idem Hendyla. | Idem (no se usa, módulo comentado). |
| `{N}publicado_facebook` | Idem Facebook. | Idem (no se publica activamente). |

`N` es el número de fila del usuario en el Excel (columna A). Ejemplo: con dos usuarios numerados `1` y `2`, el CSV tendrá `1publicado_info`, `1publicado_clasipar`, `2publicado_info`, `2publicado_clasipar`, etc.

### Reglas de filtrado para publicar

**InfoCasas** ([publicar_info.py:262](remax_2/publicar_info.py#L262)):
```
{N}publicado_info.isna()  AND  ide.notna()  AND  intentos_info < 3
```

**Clasipar** ([publicar_clasipar.py:120](remax_2/publicar_clasipar.py#L120)):
```
{N}publicado_clasipar.isna()  AND  ide.notna()  AND  intentos_clasi < 4
```

### Estados posibles de una fila

| Estado | `titulo` | `{N}publicado_*` | Significado |
|---|---|---|---|
| Recién agregada | `""` | `NaN` | Solo tiene link, ciudad, fecha. Pendiente de scrapear. |
| Scrapeada, sin publicar | con texto | `NaN` | Lista para que cualquier usuario la publique. |
| Publicada por usuario N | con texto | `'1'` | Excluida del filtro de N, sigue disponible para otros. |
| Eliminada en origen | `"Eliminado"` | `1` en todas | Fuera del scrapeo y de toda publicación. |
| Precio inválido | con texto | `'1'` silencioso | Marcada por `marcar_precios_invalidos_como_publicado` al inicio. |
