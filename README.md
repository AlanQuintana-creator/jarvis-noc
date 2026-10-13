# Jarvis NOC

Asistente abierto de texto y voz para operaciones NOC. Este repositorio se desarrolla y valida **por separado** de NOC-Plataforma; la integración se hará cuando los flujos, permisos, latencia y pruebas estén listos.

## Estado

Primera base ejecutable (v0.1): API de chat por streaming, transcripción de audio, síntesis de voz y una política de capacidades con denegación predeterminada. Todavía no hay conectores a Zabbix, GLPI ni a la plataforma NOC; Jarvis no puede ejecutar acciones operativas.

El código tiene licencia MIT. Cada modelo de IA y cada voz usados por un despliegue conservan **sus propias licencias y condiciones**.

## Principios

- El modelo genera lenguaje; los permisos se validan en código.
- Ningún dato de otro cliente puede pasar a una herramienta del asistente.
- Sin acceso a secretos ni a shell arbitrario.
- Las acciones con cambios necesitan una aprobación verificada por la plataforma y un rol autorizado.
- Proveedores de modelo, STT y TTS intercambiables mediante API compatible. Las claves permanecen en variables de entorno, nunca en Git.
- La API de Jarvis no debe exponerse directamente a Internet: en la futura integración, la consola llamará al BFF y la API NOC autenticará al usuario.

## Desarrollo local

Requiere Python 3.11 o superior.

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Configurá un `JARVIS_API_KEY` propio y los proveedores necesarios en el entorno. El archivo `.env` es una referencia para valores; Uvicorn no lo carga automáticamente. Por ejemplo:

```powershell
$env:JARVIS_API_KEY = "valor-de-desarrollo"
$env:JARVIS_MODEL_BASE_URL = "http://localhost:11434/v1"
$env:JARVIS_MODEL_API_KEY = "clave-del-proveedor-o-valor-local"
$env:JARVIS_MODEL_NAME = "modelo-instalado"
.venv\Scripts\uvicorn jarvis_noc.main:app --reload --port 8010
```

Consultar `http://localhost:8010/docs` para ver el contrato HTTP. Los endpoints de voz esperan proveedores compatibles con `/v1/audio/transcriptions` y `/v1/audio/speech`. Deben configurarse `JARVIS_STT_*` y `JARVIS_TTS_*` antes de usarlos.

```powershell
.venv\Scripts\python -m pytest
```

## Arquitectura prevista

```text
Consola Jarvis (texto y micrófono)
    → BFF de NOC-Plataforma (sesión OIDC)
    → API NOC (identidad, tenant, rol, auditoría, aprobaciones)
    → Jarvis (orquestación, políticas, contexto, voz)
    → proveedor de modelo / STT / TTS
```

Las futuras herramientas de lectura y acción se implementarán en la API NOC con contratos tipados. Jarvis enviará solicitudes de herramientas; la API volverá a validar identidad, cliente y política antes de consultar o ejecutar nada.

## Criterios previos a la integración

1. Chat y voz en español con cancelación, errores claros y streaming medido.
2. Fuentes citadas en respuestas sobre incidentes y runbooks.
3. Aislamiento multicliente probado y permisos por rol.
4. Pruebas de instrucciones maliciosas en eventos, tickets y documentos recuperados.
5. Acciones de cambio bloqueadas sin aprobación durable; auditoría de cada solicitud.
6. Evaluación con casos NOC reales anonimizados y metas de latencia definidas sobre el hardware elegido.

## Próximos incrementos

- Interfaz web de chat y pulsar para hablar, con reproducción de audio.
- Adaptadores de proveedores y prueba integral de texto y voz.
- Herramientas de solo lectura para incidentes, eventos, activos y runbooks.
- Flujo de solicitud de acción con aprobación humana y registro auditable.
- Integración con NOC-Plataforma después de cumplir los criterios anteriores.
