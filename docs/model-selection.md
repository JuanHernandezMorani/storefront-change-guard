# Seleccion de modelo

## Resumen

El Test 1 midio rendimiento y comportamiento operativo de candidatos Qwen locales. El resultado inicial favorecia a modelos 4B en throughput, memoria y tiempo de pared. Sin embargo, el flujo real de Phase 03 exigia algo mas estricto: devolver JSON completo, parseable y sustentado en evidencia.

## Resultado de Test 1

| Modelo | Lectura principal |
|---|---|
| Qwen3.5 4B Q4 | Mas rapido y liviano en rendimiento bruto. |
| Qwen3.5 4B IQ3 | Muy liviano y veloz, pero no fue el candidato final del contrato. |
| Qwen3.5 9B Q4 | Mas pesado, sin ventaja suficiente para este prototipo. |
| Qwen3.5 9B IQ3 | Balance final: suficiente capacidad para cumplir contrato con menor peso que 9B Q4. |

## Motivo del cambio

Cambie del 4B Q4 al 9B IQ3 porque el 4B produjo JSON incompleto en la ejecucion real con el parser estricto. El 9B IQ3 completo el contrato y paso los gates A-D. Para este prototipo, un resultado mas lento pero valido es mejor que una salida rapida que el sistema debe rechazar.

## Evidencia incluida

- `benchmark_results/test_1/README.md`
- `benchmark_results/test_1/plots/`
- `REPORT/executions/run-014-phase-03-model-selection.md`
- `REPORT/executions/run-015-phase-03-live-gates.md`

## Criterio final

No afirmo que el 9B IQ3 sea mejor en general. Afirmo que fue el candidato que cumplio el contrato de este prototipo: salida estructurada, evidencia verificable y gates vivos completos.
