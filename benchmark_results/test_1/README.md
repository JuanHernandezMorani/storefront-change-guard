# Resultados de benchmark - Test 1

## Proposito

Este paquete conserva la evidencia curada del Test 1 de seleccion de modelo. No es el harness crudo; es el resultado que uso para explicar la primera decision de rendimiento y el cambio posterior de modelo.

## Lectura final

Test 1 mostro que los modelos 4B tenian mejor throughput y menor memoria. Aun asi, el flujo real de Phase 03 encontro un problema: el candidato 4B no cumplio de forma confiable el contrato de JSON estructurado. Por eso mantengo estos resultados como evidencia valida de rendimiento, pero elijo el 9B IQ3 como modelo final de producto por cumplimiento de contrato.

## Artefactos incluidos

- `data/model-summary.csv` y `.json`.
- `data/prompt-summary.csv` y `.json`.
- `data/outlier-analysis.csv` y `.json`.
- `plots/` con graficos usados en la presentacion.
- `quality_review/` como apoyo a revision humana.
