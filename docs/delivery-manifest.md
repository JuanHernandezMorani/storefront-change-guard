# Manifiesto de entrega

## Incluido

- Codigo del prototipo: `agent_solution/`.
- Storefront controlado: `demo-storefront/`.
- Scripts operativos: `scripts/`.
- Politicas: `policies/`.
- Documentacion en espanol: `README.md`, `docs/`, `AUDIT/`, `REPORT/`.
- Evidencia seleccionada: `benchmark_results/`, `artifacts/phase04-live/`, `artifacts/phase05-live/`.
- Presentacion: `docs/presentation/Storefront_Change_Guard_presentacion_es.pptx`.
- Originales en ingles: `.original_en/`.

## Excluido

- Pesos GGUF y otros modelos.
- `.env`, secrets, caches y virtualenv.
- `benchmarks/` porque es harness crudo de medicion.
- `storefront_change_guard.egg-info/` porque es metadata regenerable de packaging.
- `node_modules/`, `dist/`, `.git/` y caches de herramientas.

## Regla especial

`benchmark_results/` no se excluye. Es parte del relato tecnico porque muestra el Test 1 y permite explicar por que el rendimiento inicial no fue suficiente para elegir el modelo final.
