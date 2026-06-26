# Runbook de entrega

## Objetivo

Este runbook describe como reproduzco la entrega final sin depender de artefactos ocultos. El modelo GGUF no se incluye por peso, pero el runner permite pasar la ruta local.

## Secuencia recomendada

1. Crear entorno Python con `py -3.11 -m venv .venv`.
2. Instalar el paquete editable con `python -m pip install -e ".[dev]"`.
3. Instalar dependencias del storefront con `npm ci` dentro de `demo-storefront/`.
4. Ejecutar `npm run lint`, `npm run build` y `npm test`.
5. Ejecutar `scripts/run_all_phase_validation.ps1 -Phase all`.
6. Ejecutar Phase 03 con `run_phase03_live_gates.ps1` y rutas locales de `llama-cli` y GGUF.
7. Ejecutar Phase 04 con `run_phase04_live_validation.ps1`.
8. Ejecutar Phase 05 con `run_phase05_live_decision.ps1` usando los JSON previos.

## Criterio de exito

- Phase 03 debe completar Gate A, Gate B, Gate C y Gate D.
- Phase 04 debe devolver `VALIDATED`.
- Phase 05 debe devolver `READY`.
- El checkout principal no debe quedar modificado por Phase 04 ni Phase 05.

## Limites de entrega

`benchmarks/` y `storefront_change_guard.egg-info/` se excluyen porque son regenerables o demasiado crudos para la entrega. `benchmark_results/` se incluye como evidencia curada de Test 1.
