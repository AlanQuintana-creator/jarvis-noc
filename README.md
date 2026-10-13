# Jarvis NOC

Asistente abierto de texto y voz para operaciones NOC. Este repositorio se desarrolla y valida **por separado** de NOC-Plataforma; la integración se hará cuando los flujos, permisos, latencia y pruebas estén listos.

## Estado

Primera base ejecutable (v0.1): página local de prueba con chat y micrófono, API de chat por streaming, transcripción de audio, síntesis de voz y una política de capacidades con denegación predeterminada. Todavía no hay conectores a Zabbix, GLPI ni a la plataforma NOC; Jarvis no puede ejecutar acciones operativas.

El código tiene licencia MIT. Cada modelo de IA y cada voz usados por un despliegue conservan **sus propias licencias y condiciones**.

## Principios

- El modelo genera lenguaje; los permisos se validan en código.
- Ningún dato de otro cliente puede pasar a una herramienta del asistente.
- Sin acceso a secretos ni a shell arbitrario.
- Las acciones con cambios necesitan una aprobación verificada por la plataforma y un rol autorizado.
- Proveedores de modelo, STT y TTS intercambiables mediante API compatible. Las claves permanecen en variables de entorno, nunca en Git.
- La API de Jarvis no debe exponerse directamente a Internet: en la futura integración, la consola llamará al BFF y la API NOC autenticará al usuario.

## Desarrollo local

### Docker Desktop en Windows

Esta carpeta del Escritorio es la instalación independiente de Jarvis. La aplicación corre en Docker Desktop; Groq procesa las consultas y la transcripción del micrófono. La lectura de respuestas en voz alta usa la voz del navegador. Todavía no existe conexión a la plataforma NOC.

1. Abrí Docker Desktop y esperá a que el motor indique que está funcionando. Docker Desktop en Windows requiere WSL 2 y la característica de Windows **Subsistema de Windows para Linux** habilitada.
2. En PowerShell, desde esta carpeta, ejecutá `./preparar.ps1`. Crea `.env` con una clave local aleatoria. El archivo no se sube a Git.
3. Generá una API key en [GroqCloud](https://console.groq.com/keys). Ejecutá `./configurar-groq.ps1` y pegá la clave completa cuando se solicite. No pegues esa clave en la página web.
4. Ejecutá `docker compose up -d --build` y comprobá el estado con `docker compose ps`.
5. Abrí [http://127.0.0.1:8010/demo](http://127.0.0.1:8010/demo). Copiá **JARVIS_API_KEY** desde `.env` al campo **Clave local de Jarvis** de la página. Presioná **Comprobar conexión** y enviá una pregunta. Para el micrófono, permití el acceso del navegador.

Si cambiás la clave de Groq, ejecutá de nuevo `./configurar-groq.ps1` y después `docker compose up -d --force-recreate`. Para apagar Jarvis, ejecutá `docker compose down`. La API queda accesible únicamente desde este equipo en el puerto 8010.

### Python, sin Docker

Requiere Python 3.11 o superior.

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Abrí `.env` y completá `JARVIS_API_KEY` con una clave propia. Para probar chat y micrófono con la configuración de ejemplo, conseguí una clave de [GroqCloud](https://console.groq.com/keys) y pegala en `JARVIS_MODEL_API_KEY` y `JARVIS_STT_API_KEY`. Nunca publiques ese archivo ni pegues la clave en un issue. El iniciador carga `.env` solo en el proceso local:

```powershell
.venv\Scripts\python.exe run.py
```

Abrí **http://127.0.0.1:8010/demo**. Ingresá la `JARVIS_API_KEY` de tu `.env`, presioná **Comprobar conexión** y escribí una pregunta. Para usar el micrófono, permití el acceso del navegador, presioná el botón para iniciar y detener la grabación, revisá el texto transcrito y presioná **Enviar**. La casilla **Leer respuesta en voz alta** usa la voz disponible en el navegador. La clave ingresada en la página permanece solo en la memoria de esa pestaña.

La API se documenta en `http://127.0.0.1:8010/docs`. Los endpoints de voz también permiten un proveedor TTS compatible con `/v1/audio/speech`, configurando `JARVIS_TTS_*`.

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

- Pruebas integrales con proveedores reales y evaluación de latencia de texto y voz.
- Herramientas de solo lectura para incidentes, eventos, activos y runbooks.
- Flujo de solicitud de acción con aprobación humana y registro auditable.
- Integración con NOC-Plataforma después de cumplir los criterios anteriores.
