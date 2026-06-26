# Arquitectura

## Principio principal

Divido autoridad y ejecucion. El modelo local ayuda a analizar, pero el sistema deterministico decide que se acepta y que se rechaza.

## Flujo

```text
intake -> evidencia -> modelo local -> validador -> parche aislado -> readiness
```

## Componentes

| Componente | Responsabilidad |
|---|---|
| Intake | Clasifica la solicitud y detecta alcance, idioma y restricciones. |
| Git context | Junta evidencia acotada de archivos modificados o solicitados. |
| Analysis | Ejecuta un unico modelo local y espera JSON estructurado. |
| Validator | Rechaza salidas invalidas o sin evidencia. |
| Patch validation | Aplica un diff suministrado en worktree separado. |
| Readiness policy | Decide `READY`, `NOT_READY` o `INSUFFICIENT_EVIDENCE`. |

## Fronteras de confianza

El modelo no tiene shell ni autoridad de merge. Los comandos de validacion estan allowlistados. La decision final no depende de texto libre del modelo sino de artefactos JSON previos.
