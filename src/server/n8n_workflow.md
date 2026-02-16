# n8n Workflow Structure

This document outlines the logic for the n8n workflow. Since you are self-hosting n8n, you can visually build this or import a JSON if I were to generate the full JSON blob (which can be verbose/fragile). Here is the logical structure and the JSON parts for the key nodes.

## Workflow Overview

1.  **Webhook Node**: Listen on `POST /webhook/monitor`.
2.  **Auth Node (Optional/Manual)**: Check `x-api-key` header.
3.  **Switch Node**: Route based on `body.action` (for INICIO/FIN) or existence of `body.activities` (for monitoring data).

## Nodes Detail

### 1. Webhook
- **Path**: `/webhook/monitor`
- **Method**: `POST`
- **Authentication**: Header Auth (match `x-api-key`).

### 2. Switch (Router)
- **Expression**: `{{ $json.body.action ? 'attendance' : 'activity' }}`
- **Output 0 (Attendance)**: `INICIO_JORNADA` or `FIN_JORNADA`
- **Output 1 (Activity)**: Bulk data from `monitor_core`.

### 3. Route: Attendance (Output 0)
- **Postgres Node (Supabase)**:
    - **Operation**: Insert
    - **Schema**: `public`
    - **Table**: `attendance_log`
    - **Columns**:
        - `employee_id`: `{{ $json.body.pc_name }}`
        - `event_type`: `{{ $json.body.action == 'INICIO_JORNADA' ? 'INICIO' : 'FIN' }}`
        - `timestamp`: `{{ $now }}` (or from payload)

### 4. Route: Activity (Output 1)
- **Split Out Node**:
    - **Field to Split Out**: `body.activities`
- **Postgres Node (Supabase)**:
    - **Operation**: Insert
    - **Schema**: `public`
    - **Table**: `activity_log`
    - **Columns**:
        - `employee_id`: `{{ $('Webhook').item.json.body.pc_name }}` (Reference parent node for PC Name)
        - `window_title`: `{{ $json.window_title }}`
        - `duration_seconds`: `{{ $json.duration_seconds }}`
        - `created_at`: `{{ $now }}`

## Supabase Connection
- Use the **Postgres** node in n8n.
- **Host**: `db.your-project-ref.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `[YOUR_DB_PASSWORD]`
- **SSL**: Enable SSL (Supabase requires it).

---

## JSON Snippet for Import (Skeleton)

```json
{
  "nodes": [
    {
      "parameters": {
        "path": "monitor",
        "responseMode": "lastNode",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "dataType": "string",
        "value1": "={{ $json.body.action }}",
        "rules": {
          "rules": [
            {
              "value2": "INICIO_JORNADA"
            },
            {
              "value2": "FIN_JORNADA"
            }
          ]
        },
        "fallbackOutput": 1
      },
      "name": "Switch",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "table": "attendance_log",
        "columns": "employee_id, event_type",
        "options": {}
      },
      "name": "Insert Attendance",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 1,
      "position": [900, 200]
    },
    {
      "parameters": {
        "fieldToSplitOut": "body.activities",
        "options": {}
      },
      "name": "SplitOut",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 1,
      "position": [900, 400]
    },
    {
      "parameters": {
        "table": "activity_log",
        "columns": "employee_id, window_title, duration_seconds",
        "options": {}
      },
      "name": "Insert Activity",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 1,
      "position": [1100, 400]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Switch",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Switch": {
      "main": [
        [
          {
            "node": "Insert Attendance",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "SplitOut",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "SplitOut": {
      "main": [
        [
          {
            "node": "Insert Activity",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```
