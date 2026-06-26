# Politica de trazabilidad de fases, fixes y enhancements

Uso esta politica para que cada cambio tenga propietario claro.

## Identificadores

| Identificador | Uso |
|---|---|
| `Phase-NN` | Nueva fase de implementacion o validacion. |
| `Phase-NN-FIX-NN` | Correccion de un defecto originado en esa fase. |
| `Phase-NN-ENHANCE-NN` | Mejora no bloqueante asociada a esa fase. |
| `Phase-NN-REVIEW-NN` | Review que verifica o exige cambios. |

## Regla principal

Un fix pertenece a la fase donde se origino el problema, aunque lo detecte mas tarde. Si Phase 05 detecta un defecto creado en Phase 02, lo registro como `Phase-02-FIX-NN`.

## Contenido obligatorio de cada fix/enhance

Registro motivo, disparador, causa raiz, alternativas consideradas, razon de la solucion elegida y validacion.
