# Registro de cambios

## [0.6.0] - 2026-06-26

### Agregado

- Agregue la audiencia final `Phase-06-REVIEW-01` para verificar reglas de trazabilidad, cobertura del reto, README, decision document, PowerPoint y limites de entrega.
- Agregue la presentacion en PowerPoint en espanol con resumen ejecutivo, arquitectura, capacidades, cambio de modelo, graficos de Test 1 y plan de demo.
- Agregue `docs/decision-document.pdf` como version de lectura del documento de decisiones.
- Preserve la documentacion original en ingles dentro de `.original_en/`.

### Cambiado

- Actualice la documentacion principal a espanol para el publico de exposicion.
- Actualice el README con instalacion y ejecucion paso a paso.
- Reubique la narrativa final alrededor de evidencia reproducible: Test 1 permanece como benchmark de rendimiento, mientras que el cambio a 9B queda justificado por cumplimiento del contrato estructurado.

### Verificado

- `benchmarks/` y `storefront_change_guard.egg-info/` estan cubiertos por `.gitignore` y son seguros de excluir de la entrega.
- `benchmark_results/` queda incluido porque contiene la evidencia seleccionada del Test 1.
- El estado final cubre las cuatro capacidades solicitadas por el reto.

## [0.5.0] - 2026-06-26

- Consolide runners de entrega, Phase 04, Phase 05, Phase 06 y artefactos vivos.
- Seleccione `Qwen3.5-9B-UD-IQ3_XXS.gguf` como runtime de producto despues de evidencia controlada.
- Corregi identidad de modelo, scope explicito, cache y lectura JSON UTF-8 sin BOM.

## [0.4.0] - 2026-06-26

- Agregue validacion aislada de parches y politica deterministica de readiness.
- Endureci el limite de stdout de `llama-cli` y el manejo del envelope de razonamiento.

## [0.3.0] - 2026-06-24

- Agregue analisis semantico local con evidencia, cache y validacion estructurada.

## [0.2.1] - 2026-06-24

- Agregue contexto Git, fingerprint y excerpts acotados.

## [0.2.0] - 2026-06-24

- Corregi contrato de intake y deteccion deterministica de objetivos mixtos.

## [0.1.0] - 2026-06-23

- Inicialice el proyecto, el storefront controlado y el primer intake gate.
