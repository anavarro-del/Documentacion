# DataFilterManager — Guía rápida

Este README  documenta el uso básico del gestor de filtros de datos `DataFilterManager` mostrado en el extracto.

## Propósito

`DataFilterManager` es una utilidad para crear, inspeccionar y aplicar subconjuntos (subsets) basados en condiciones textuales sobre un DataFrame (por ejemplo, Pandas). Está pensada para: exploración rápida, depuración de reglas de filtrado y aplicación controlada de filtros al conjunto "principal".

## Características principales

- Crear subsets a partir del DataFrame principal filtrando por palabras o expresiones sobre una columna (p. ej. `descripcion`).
- Ver el top de palabras en cualquier subset para analizar su contenido.
- Agregar palabras a excluir para refinar filtros.
- Filtrar un subset para crear un nuevo subset encadenado.
- Aplicar un subset como filtro al DataFrame principal (eliminar filas del principal).
- Restaurar el principal si se cometen errores.
- Listar y recuperar subsets por nombre.

## Inicialización

Asumiendo que tienes un DataFrame llamado `df_plasticos` y una columna identificadora `identifier_item`:

```python
manejador = DataFilterManager(df_plasticos, 'identifier_item')
```

Parámetros:
- df: DataFrame original (pandas.DataFrame).
- id_col: nombre de la columna que identifica filas (usada internamente para mantener integridad al filtrar).

## API (métodos relevantes)

- manejador.ver_top_palabras(nombre_subset='principal', top_n=25, excluir_palabras=None)
  - Muestra las palabras más frecuentes en el subset indicado.
  - Si `nombre_subset` no se pasa, muestra el top del `principal`.

- manejador.get_principal()
  - Devuelve el DataFrame `principal` actual (después de aplicar filtros si los hubo).

- manejador.reset_principal()
  - Restaura el `principal` al estado inicial (antes de aplicar filtros).

- manejador.listar_subsets()
  - Lista los nombres de todos los subsets disponibles (incluyendo `principal`).

- manejador.filtrar_por_palabra(columna, palabra, nombre='nuevo_subset')
  - Crea un nuevo subset que contiene las filas donde `columna` contiene `palabra`.
  - `palabra` puede ser una cadena simple o expresión; el método puede normalizar a minúsculas antes de comparar.

- manejador.agregar_excluidos(nombre_subset, lista_palabras)
  - Añade palabras a excluir para un subset (filtrado posterior las ignora).

- manejador.filtrar_subset(nombre_origen, columna, palabra, nombre='nuevo_subset')
  - A partir del subset `nombre_origen`, crea un nuevo subset aplicando otro filtro sobre `columna`.

- manejador.aplicar_filtro(nombre_subset)
  - Elimina del DataFrame `principal` las filas contenidas en `nombre_subset` (aplica filtro definitivo).

- manejador.get_subset(nombre_subset)
  - Devuelve el DataFrame correspondiente al subset solicitado.

## Ejemplo paso a paso (basado en el fragmento)

1. Ver el top de palabras del `principal` (sin parámetros):

```python
manejador.ver_top_palabras()
```

2. Inicializar el gestor:

```python
manejador = DataFilterManager(df_plasticos, 'identifier_item')
```

3. Crear un subset buscando la palabra "parte" en la columna `descripcion`:

```python
manejador.filtrar_por_palabra('descripcion', 'parte', nombre='partes')
```

4. Inspeccionar el subset recién creado:

```python
manejador.ver_top_palabras('partes', top_n=20)
```

5. Añadir palabras a excluir del subset `partes`:

```python
manejador.agregar_excluidos('partes', ['caja', 'plastico', 'de'])
```

6. Crear un nuevo subset filtrando el subset `partes` por otra palabra:

```python
manejador.filtrar_subset('partes', 'descripcion', 'medico', nombre='partes_medicas')
```

7. Revisar y, si es correcto, aplicar el filtro al `principal`:

```python
manejador.ver_top_palabras('partes_medicas', top_n=15)
manejador.aplicar_filtro('partes_medicas')
print(f"Filas restantes en principal: {len(manejador.df_principal)}")
```

8. Si te equivocaste, restaurar el `principal`:

```python
manejador.restaurar_todo()
```

8. Si te equivocaste, restaurar el `paso anterior`:

```python
manejador.restaurar_anterior()
```

## Buenas prácticas y notas

- Inspecciona siempre con `ver_top_palabras` antes de aplicar un filtro definitivo con `aplicar_filtro`.
- Usa `agregar_excluidos` para quitar palabras no relevantes y reducir falsos positivos.
- Mantén un `id_col` consistente para evitar eliminar o duplicar filas por error.
- Considera exportar tus subsets para auditoría antes de aplicar filtros permanentes.

## Ejemplo rápido de trabajo repetible

1. Crear subset -> 2. Ver top -> 3. Ajustar excluidos -> 4. Crear subset refinado -> 5. Ver top -> 6. Aplicar filtro -> 7. Guardar cambios o revertir.

## Preguntas frecuentes (FAQ)

- P: ¿Esto modifica mi DataFrame original? 
  R: El diseño habitual es que el `principal` se mantiene en memoria dentro del manejador y `aplicar_filtro` lo modifica; siempre hay `reset_principal` para volver atrás.

- P: ¿Se pueden encadenar filtros? 
  R: Sí: `filtrar_subset` permite crear subsets a partir de otros subsets.

- P: ¿Qué pasa con mayúsculas/minúsculas y acentos? 
  R: Depende de la implementación interna; se recomienda normalizar texto (a minúsculas y normalizar acentos) antes de filtrar.

## Licencia y atribución

Incluye aquí la licencia que prefieras (p. ej. MIT) o indica que el README es documentación interna.

---

Si quieres, puedo:
- Ajustar el README para que sea un `README.md` en la raíz del proyecto.
- Añadir ejemplos con código real (creando un DataFrame de ejemplo y mostrando la salida esperada).
- Generar tests unitarios mínimos para las operaciones del gestor.

Dime qué prefieres y lo actualizo.



