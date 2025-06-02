import logging
import xmltodict
import requests
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from .const import DOMAIN, DEFAULT_NAME, DEFAULT_ORP, XML_URL

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME, DEFAULT_NAME)
    orp = config.get("orp", DEFAULT_ORP)
    add_entities([ChmuAlertsSensor(name, orp)], True)

class ChmuAlertsSensor(SensorEntity):
    def __init__(self, name, orp_code):
        self._name = name
        self._orp_code = orp_code
        self._state = "Žádné výstrahy"
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        try:
            response = requests.get(XML_URL, timeout=10)
            response.raise_for_status()
            data = xmltodict.parse(response.content)

            alerts = data.get("alert", {}).get("info", [])
            if not isinstance(alerts, list):
                alerts = [alerts]

            relevant_alerts = []
            for alert in alerts:
                if alert.get("language", "").lower() != "cs":
                    continue
                description = alert.get("description")
                if not description or not description.strip():
                    continue

                areas = alert.get("area", [])
                if not isinstance(areas, list):
                    areas = [areas]

                for area in areas:
                    geocodes = area.get("geocode", [])
                    if not isinstance(geocodes, list):
                        geocodes = [geocodes]

                    for geocode in geocodes:
                        if geocode.get("value") == self._orp_code:
                            relevant_alerts.append({
                                "event": alert.get("event", "Neznámý jev"),
                                "description": description.strip(),
                                "instruction": alert.get("instruction", "Bez doporučení"),
                                "start": alert.get("onset", "Neznámý začátek"),
                                "end": alert.get("expires", "Neznámý konec"),
                                "severity": alert.get("severity", "Neznámá"),
                                "certainty": alert.get("certainty", "Neznámá"),
                                "urgency": alert.get("urgency", "Neznámá"),
                                "headline": alert.get("headline", "Bez nadpisu")
                            })

            if relevant_alerts:
                self._state = relevant_alerts[0]["event"]
                self._attributes = {
                    "alerts": relevant_alerts,
                    "count": len(relevant_alerts)
                }
            else:
                self._state = "Žádné výstrahy"
                self._attributes = {"alerts": [], "count": 0}

        except Exception as e:
            _LOGGER.error(f"Chyba při stahování dat z ČHMÚ: {e}")
            self._state = "Chyba"
