# DPlusSimulator

Schaltet ein zugewiesenes Relais anhand der Batteriespannung und simuliert damit ein D+-Signal auf Venus OS.

## Installation

[SetupHelper](https://github.com/kwindrem/SetupHelper) installieren. Im Paketmanager: Paket `DPlusSimulator`, GitHub-Benutzer `CoYoDuDe`, Branch `main`.

## Einrichtung

1. **Einstellungen → DPlusSimulator** öffnen.
2. Spannungsquelle und tatsächlich angeschlossenes Relais wählen.
3. Ein-/Ausschaltspannung und Verzögerungen zum eigenen System passend einstellen.
4. Funktion prüfen, danach den Dienst einschalten.

Neue Installationen starten **deaktiviert und ohne zugewiesenes Relais**. Die automatische Spannungsquelle kann z. B. BMV oder SmartShunt nutzen. Ein verwendetes BMV-Relais muss auf „Manuell“ stehen. Relaisnummern beginnen bei 1; ein leeres Feld bedeutet kein Ausgang. Der GPIO-Modus simuliert intern und schaltet derzeit keinen physischen GPIO.

## Startwerte

| System | Einschalten | Ausschalten |
|---|---:|---:|
| 12 V | 13,2 V | 12,8 V |
| 24 V | 26,4 V | 25,6 V |

Die voreingestellten Werte gelten für 12 V. Bei 24 V auch die Not-Aus-Schwelle passend einstellen. Ohne gültige Spannung bleibt die Steuerung aus.

Optional kann Zündplus berücksichtigt werden: Einschalten braucht dann Zündung und Einschaltspannung; bei Zündung aus wird sofort ausgeschaltet. Während Zündung an wird die normale Ausschaltspannung ignoriert. Bei sehr niedriger Spannung greift weiterhin der verzögerte Not-Aus. Manuelle Steuerung ist im Menü möglich.

## Updates und Entfernen

Über SetupHelper installieren, aktualisieren und entfernen. Bestehende Einstellungen bleiben erhalten. Ältere Paketnamen werden einmalig auf **DPlusSimulator** umgestellt und privat gesichert; alte und neue Pakete nicht parallel installieren. Der Paketordner heißt `/data/DPlusSimulator`, Einstellungen liegen unter `/data/setupOptions/DPlusSimulator`.

## Unterstützung

Die Pakete sind kostenlos. Freiwillige Unterstützung: [PayPal](https://paypal.me/CoYoDuDe), [Buy Me a Coffee](https://www.buymeacoffee.com/CoYoDuDe), [weitere Projekte](https://dnsmith.net/). Kein Abo-Zwang.
