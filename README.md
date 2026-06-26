# Storefront Change Guard

Prototipo local-first para revisar cambios de codigo de un storefront e-commerce, validar correcciones en un entorno aislado y decidir readiness con una politica deterministica.

## Estado final de entrega

Entrego el proyecto como un prototipo acotado y reproducible. La salida del modelo local es consultiva: la recoleccion de evidencia, la validacion del parche y la decision final quedan bajo reglas deterministicas.

| Fase | Trabajo principal | FIX / ENHANCE asociados | Review que verifica | Estado | Evidencia |
|---|---|---|---|---|---|
| `Phase-00` | Baseline del repositorio | `Sin FIX/ENHANCE` | `Phase-06-REVIEW-01` | VERIFIED | Base tecnica y alcance inicial del storefront controlado. |
| `Phase-01` | Preparacion del storefront demo | `Phase-01-FIX-01, Phase-01-FIX-02` | `Phase-01-REVIEW-01, Phase-01-REVIEW-02, Phase-06-REVIEW-01` | VERIFIED | Reglas de shipping, pruebas del dominio monetario y separacion de contexto/hook. |
| `Phase-02` | Intake y contexto Git | `Phase-02-FIX-01, Phase-02-FIX-02, Phase-02-FIX-02 post-review` | `Phase-02A-REVIEW-01, Phase-02-REVIEW-02, Phase-06-REVIEW-01` | VERIFIED | Clasificacion de intencion, alcance explicito, preguntas acotadas y evidencias Git. |
| `Phase-03` | Analisis local con evidencia | `Phase-03-FIX-01, FIX-02, FIX-03, FIX-06, FIX-07, FIX-08, FIX-09, FIX-10` | `Phase-06-REVIEW-01` | VERIFIED | Modelo local unico, JSON estricto, cache seguro, scope explicito y gates A-D. |
| `Phase-04` | Validacion aislada de parche | `Sin FIX/ENHANCE` | `Phase-06-REVIEW-01` | VERIFIED | Parche unificado suministrado, worktree separado, comandos allowlist y artefacto VALIDATED. |
| `Phase-05` | Politica deterministica de readiness | `Sin FIX/ENHANCE` | `Phase-06-REVIEW-01` | VERIFIED | Decision READY desde JSON previos, sin modelo, sin shell nuevo y sin mutar checkout. |
| `Phase-06` | Preparacion de entrega | `Phase-06-ENHANCE-01` | `Phase-06-REVIEW-01` | VERIFIED | Documentacion en espanol, PowerPoint, decision document, manifiesto y ZIP final. |

## Capacidades demostradas

El reto pide demostrar al menos dos capacidades. Yo demuestro las cuatro, pero mantengo el alcance controlado:

| Capacidad del reto | Como la demuestro | Evidencia principal |
|---|---|---|
| Revisar cambios de codigo y dar feedback accionable | Phase 03 genera un analisis estructurado con hallazgos, severidad, evidencia y limites. | `REPORT/executions/run-015-phase-03-live-gates.md` |
| Detectar un problema y proponer una correccion con validacion | Phase 04 valida un parche unificado suministrado en worktree separado. | `artifacts/phase04-live/run-20260626-032234/` |
| Responder preguntas sobre codigo o documentacion | Gate C acepta una pregunta en español con archivo explicito y evidencia acotada. | `REPORT/executions/run-015-phase-03-live-gates.md` |
| Decidir si un cambio esta listo para avanzar | Phase 05 devuelve `READY` aplicando una politica fija sobre artefactos previos. | `artifacts/phase05-live/run-20260626-033155/` |

## Arquitectura resumida

```text
solicitud
  -> intake deterministico y evidencia Git acotada
  -> un modelo local Qwen para analisis estructurado
  -> validacion deterministica de JSON y referencias de evidencia
  -> parche suministrado aplicado en worktree separado
  -> comandos de validacion allowlist
  -> politica deterministica de readiness
```

## Limites de confianza

- El modelo puede analizar evidencia suministrada, pero no puede ejecutar shell, aplicar parches, commitear, pushear ni aprobar readiness.
- El validador rechaza JSON invalido, claims sin evidencia o referencias fuera del bundle.
- La validacion de parches solo acepta un diff unificado suministrado y lo aplica en un worktree separado.
- La politica de readiness consume JSON previos. No llama al modelo ni ejecuta nuevas pruebas.

## Cambio de modelo y criterio real de seleccion

El Test 1 mostro que el modelo 4B era mas rapido y liviano en throughput bruto. Sin embargo, al ejecutar el flujo real de producto, el modelo 4B fallo de forma repetida en el contrato de salida estricta: generaba JSON incompleto despues de normalizar el wrapper. Por eso cambie al modelo `Qwen3.5-9B-UD-IQ3_XXS.gguf`, que completó el contrato estructurado y pasó los gates A-D de Phase 03.

Esta decision no descalifica Test 1. Test 1 sigue incluido en `benchmark_results/test_1/` porque evidencia el primer criterio de rendimiento. El cambio posterior documenta un hallazgo real de operabilidad: para este prototipo, cumplir el contrato JSON y los gates pesa mas que ganar tokens por segundo.

## Instalacion paso a paso

### 1. Requisitos

- Python 3.11.
- Node.js y npm para el storefront demo.
- `llama.cpp` local con `llama-cli.exe`. Se uso un build vulkan en el entorno de produccion.
- El GGUF seleccionado en una ruta local. El peso del modelo no se incluye en el ZIP.

### 2. Crear entorno Python

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Configurar runtime local

```powershell
Copy-Item .env.example .env
```

Luego editar `.env` para apuntar al ejecutable local de `llama-cli.exe`. El modelo puede quedar en `agent_solution/model/` o pasarse con `-Model` al runner de Phase 03.

### 4. Instalar y validar el storefront demo

```powershell
cd demo-storefront
npm ci
npm run lint
npm run build
npm test
cd ..
```

### 5. Ejecutar validacion deterministica del prototipo

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts
un_all_phase_validation.ps1 `
  -Phase all
```

### 6. Ejecutar los gates vivos de Phase 03

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts
un_phase03_live_gates.ps1 `
  -LlamaCli "C:\path	o\llama-cli.exe" `
  -Model ".agent_solution\model\Qwen3.5-9B-UD-IQ3_XXS.gguf"
```

El runner valida cuatro casos: review exitosa, cache hit, pregunta en espanol con archivo explicito e insuficiencia de evidencia para un objetivo inexistente.

### 7. Ejecutar Phase 04 y Phase 05

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts
un_phase04_live_validation.ps1 `
  -Repository $PWD `
  -BaseRef HEAD
```

Despues uso el artefacto de analisis de Phase 03 y el artefacto de validacion de Phase 04:

```powershell
$analysisArtifact = ".artifacts\phase03-live\<run>\gate-a\stdout.json"
$validationArtifact = ".artifacts\phase04-live\<run>\phase04-<id>.validation.json"

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts
un_phase05_live_decision.ps1 `
  -Repository $PWD `
  -AnalysisArtifact $analysisArtifact `
  -PatchValidationArtifact $validationArtifact
```

## Estructura del repositorio

```text
agent_solution/       Implementacion Python y tests
demo-storefront/      Storefront controlado para el escenario e-commerce
scripts/              Runners operativos versionados
docs/                 Arquitectura, decisiones, runbook y presentacion
AUDIT/                Trazabilidad por fase, fix, enhance y review
REPORT/               Registros de ejecucion, prompts y uso de IA
benchmark_results/    Evidencia del Test 1 de seleccion de modelo
artifacts/            Evidencia viva seleccionada de Phase 04 y Phase 05
policies/             Politica machine-readable de readiness
.original_en/         Documentacion original en ingles preservada
```

## Politica de entrega y Git

`benchmarks/` y `storefront_change_guard.egg-info/` son seguros para ignorar y excluir porque contienen harness crudo, metadata regenerable y archivos transitorios de empaquetado. `benchmark_results/` se mantiene incluido porque contiene la evidencia seleccionada del Test 1.

La entrega excluye pesos de modelo, `.env`, cache, virtualenv, metadata Git, harness crudo de benchmarks y artefactos regenerables de packaging. La entrega conserva codigo, tests, scripts, documentacion en espanol, evidencias seleccionadas, politicas y resultados de benchmark ya consolidados.

## Documentos principales

- `docs/presentation/Storefront_Change_Guard_presentacion_es.pptx`: presentacion para la exposicion.
- `AUDIT/phase-06-REVIEW-01-final-audience-and-delivery-verification.md`: audiencia final de reglas y entrega.
- `docs/delivery-runbook.md`: secuencia de reproduccion y verificacion.
