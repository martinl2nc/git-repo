# Guía de Configuración - Dashboard Retool

## Componentes requeridos
| Componente | Tipo | Nombre |
|---|---|---|
| Selector de fechas | Date Range | `dateRange1` |
| Tabla principal | Table | `asistenciaTable` |
| Modal corrección | Modal | `modalCorreccion` |
| Input de hora | Time Input | `timeInput1` (dentro del modal) |
| Botón guardar | Button | `btnGuardar` (dentro del modal) |

---

## A. Configuración de Consultas (Resource Queries)

### Query 1: `getEmpleados`
> Resource: Supabase | Mode: SQL | Run automatically: ✅

```sql
SELECT empleado FROM view_lista_empleados;
```

---

### Query 2: `getAsistencia`
> Resource: Supabase | Mode: SQL | Run automatically: ✅

```sql
SELECT * FROM view_asistencia_diaria
WHERE fecha BETWEEN {{ dateRange1.value.start }} AND {{ dateRange1.value.end }}
  AND ({{ !empleadoDropdown.value }} OR empleado = {{ empleadoDropdown.value }})
ORDER BY fecha DESC, empleado;
```

> **Nota:** Ambos filtros trabajan juntos. Si `empleadoDropdown` está vacío, muestra todos. El `dateRange1` siempre filtra por rango de fechas. Asegúrate de que tanto `dateRange1` como `empleadoDropdown` tengan **On change → Trigger `getAsistencia`**.

---

### Query 3: `postCorreccionSalida` (UPSERT Inteligente)
> Resource: Supabase | Mode: SQL | Run automatically: ❌

```sql
-- Esto actualiza el registro si ya existe, o lo inserta si no existe.
WITH upsert AS (
    UPDATE attendance_log 
    SET timestamp = ({{ asistenciaTable.selectedRow.fecha }}::date || ' ' || {{ timeInput1.value }}::time)::timestamp AT TIME ZONE 'America/Lima'
    WHERE employee_id = {{ asistenciaTable.selectedRow.empleado }} 
      AND event_type = 'FIN' 
      AND (timestamp AT TIME ZONE 'America/Lima')::date = {{ asistenciaTable.selectedRow.fecha }}::date
    RETURNING *
)
INSERT INTO attendance_log (employee_id, event_type, timestamp)
SELECT 
    {{ asistenciaTable.selectedRow.empleado }}, 
    'FIN', 
    ({{ asistenciaTable.selectedRow.fecha }}::date || ' ' || {{ timeInput1.value }}::time)::timestamp AT TIME ZONE 'America/Lima'
WHERE NOT EXISTS (SELECT 1 FROM upsert);
```

**Explicación:** 
1. Primero intenta actualizar cualquier registro `FIN` existente para el mismo empleado y fecha.
2. Si el `UPDATE` no afectó a ninguna fila (porque no había salida), el `INSERT` final se ejecuta e inserta la marca nueva.
3. Esto evita duplicados y permite corregir una hora ya registrada.

**On Success handler:**
1. Trigger `getAsistencia` (refrescar tabla)
2. Close `modalCorreccion`
3. Optional: `utils.showNotification({title: "Éxito", description: "Asistencia actualizada", notificationType: "success"})`

---

## B. Configuración de Componentes

### `dateRange1` — Selector de fechas

| Propiedad | Valor |
|---|---|
| Start date default | `{{ moment().startOf('month').format('YYYY-MM-DD') }}` |
| End date default | `{{ moment().endOf('month').format('YYYY-MM-DD') }}` |
| On change | Trigger `getAsistencia` |

---

### `asistenciaTable` — Tabla principal

| Propiedad | Valor |
|---|---|
| Data source | `{{ getAsistencia.data }}` |

**Columnas:**

| Key | Label | Tipo |
|---|---|---|
| `empleado` | Empleado | Text |
| `fecha` | Fecha | Date |
| `hora_entrada` | Entrada | Text |
| `hora_salida` | Salida | Text |
| `horas_trabajadas` | Horas | Number |
| `estado` | Estado | Tag |

**Columna Estado (Tag colors):**

| Valor | Color |
|---|---|
| `FINALIZADO` | 🟢 Green / Success |
| `EN CURSO` | 🔵 Blue / Primary |
| `OLVIDO SALIDA` | 🔴 Red / Danger |

**Columna de Acción (agregar columna tipo "Button"):**

| Propiedad | Valor |
|---|---|
| Label | `Corregir` |
| On click | `modalCorreccion.open()` |

> El botón está siempre habilitado para cualquier fila. Al hacer clic, se abre el modal para registrar una marca de salida manual.

---

### 3. **Statistic** cards (KPIs)

**Card 1 - En Curso:**
```js
{{ getAsistencia.data.estado.filter(e => e === 'EN CURSO').length }}
```

**Card 2 - Colaboradores Totales:**
```js
{{ getAsistencia.data.empleado.length }}
```

**Card 3 - Promedio Horas (Solo finalizados):**
```js
{{ (getAsistencia.data.horas_trabajadas.reduce((sum, h) => sum + Number(h || 0), 0) / (getAsistencia.data.horas_trabajadas.filter(h => h !== null && h > 0).length || 1)).toFixed(2) }}
```

**On click del botón "Corregir" (en la tabla):**
`modalCorreccion.open()`

---

### `modalCorreccion` — Modal de corrección

**Título del modal:**
```
Corregir salida - {{ asistenciaTable.selectedRow.empleado }}
```

**Contenido dentro del modal:**

1.  **Text** (informativo):
    ```
    Empleado: {{ asistenciaTable.selectedRow.empleado }}
    Fecha: {{ asistenciaTable.selectedRow.fecha }}
    Entrada: {{ asistenciaTable.selectedRow.hora_entrada }}
    ```

2.  **`timeInput1`** — Input de hora:
    | Propiedad | Valor |
    |---|---|
    | Label | Hora de salida |
    | Format | `HH:mm` |
    | Default value | `18:00` |

3.  **`btnGuardar`** — Botón:
    | Propiedad | Valor |
    |---|---|
    | Label | 💾 Guardar corrección |
    | Color | Primary |
    | On click | Trigger `postCorreccionSalida` |

---

## C. Flujo de uso

```
1. Usuario abre el dashboard
2. Selecciona rango de fechas en dateRange1
3. La tabla muestra los registros filtrados
4. Hay una columna con boton "CORREGIR":
   a. Click → Se abre modalCorreccion
   b. Ingresa hora de salida
   c. Click "Guardar corrección"
   d. Se inserta registro FIN en attendance_log
   e. Tabla se refresca automáticamente
   f. Estado cambia a "FINALIZADO"
```
