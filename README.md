# ČHMÚ Výstrahy

Integrace pro zobrazení výstrah z ČHMÚ podle ORP kódu (např. Prostějov).

## Instalace

1. Přidej tento repozitář jako vlastní repozitář do HACS.
2. Nainstaluj integraci.
3. Přidej do `configuration.yaml`:

```yaml
sensor:
  - platform: chmu_alerts
    name: "ČHMÚ Výstrahy Prostějov"
    orp: "5202"
```

4. Restartuj Home Assistant.

## Atributy senzoru

- `alerts`: seznam aktuálních a budoucích výstrah
- `count`: počet výstrah
