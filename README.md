# DPlusSimulator

DPlusSimulator ist ein SetupHelper-Paket fuer Venus OS. Es installiert einen Dienst zur Simulation eines D+-Signals und bindet eine Einstellungsseite ins alte Venus-GUI-v1 ein.

## Voraussetzungen

- [SetupHelper](https://github.com/kwindrem/SetupHelper) von [kwindrem](https://github.com/kwindrem) aktuell installiert

# DPlusSimulator

DPlusSimulator ist ein SetupHelper-Paket für Venus OS.  
Es simuliert ein D+-Signal abhängig von der Batteriespannung.

## Voraussetzungen

- SetupHelper installiert
- Eine Batteriespannung auf dem Victron-D-Bus (z. B. BMV oder SmartShunt)

## Installation

Repository im SetupHelper als Custom-Paket eintragen und über den PackageManager installieren.

Paketname: `DPlusSimulator`, GitHub-Benutzer: `CoYoDuDe`, Branch: `main`.
Ab v1.2 lauten Paketordner `/data/DPlusSimulator`, Optionenordner
`/data/setupOptions/DPlusSimulator`, Dienst `com.coyodude.DPlusSimulator` und
Einstellungsprefix `/Settings/Devices/DPlusSimulator`. Der Installer uebernimmt
alte Einstellungen einmalig, entfernt die alte Installation mit SetupHelper
und bewahrt das Altpaket unter dem neuen Optionenordner als Migration-Backup.
Bereits vorhandene Einstellungen am neuen Prefix werden nicht ueberschrieben.
Das Paket muss unter seinem neuen Namen installiert werden; doppelte alte/neue
Eintraege werden vor der Migration abgewiesen. Aktualisierung und Deinstallation
laufen danach ausschliesslich unter `DPlusSimulator`.

## Zündplus (optional)

Optional kann ein Zündplus-Signal berücksichtigt werden.

Wenn aktiviert:
- Einschalten nur bei:
  - Spannung >= `OnVoltage`
  - und Zündung AN
- Ausschalten:
  - Zündung AUS → sofort AUS
- Während Zündung AN:
  - `OffVoltage` wird ignoriert

Not-Aus:
- Bei sehr niedriger Spannung (`EmergencyOffVoltage`)
- mit kurzer Verzögerung (`EmergencyOffDelaySec`)

## Hinweise

- Der Dienst benötigt eine gültige Spannungsquelle auf dem D-Bus
- Ohne Spannung arbeitet der Simulator nicht
- Manuelle Steuerung im GUI möglich
- BMV-Relay muss auf „Manuell“ stehen, wenn es verwendet wird

## Empfohlene Startwerte

12V-System:
- `OnVoltage`: 13.2
- `OffVoltage`: 12.8

24V-System:
- `OnVoltage`: 26.4
- `OffVoltage`: 25.6

## Unterstützung

Dieses Projekt wird unabhängig und privat entwickelt und kostenlos bereitgestellt. Freiwillige Unterstützung hilft bei Infrastruktur, Servern, Domains, Tests, Wartung und Weiterentwicklung.

- [PayPal](https://paypal.me/CoYoDuDe)
- [Buy Me a Coffee](https://www.buymeacoffee.com/CoYoDuDe)
- [Weitere Projekte und Informationen](https://dnsmith.net/)

Unterstützung ist freiwillig. Es gibt keinen Abo-Zwang und daraus entsteht kein Anspruch auf bestimmte Funktionen oder persönlichen Support.

## Inbetriebnahme ab v1.1

Neue Installationen starten deaktiviert und ohne zugewiesenes Relais. Zuerst die Starterspannungsquelle und das tatsaechlich verdrahtete Relais pruefen, danach aktivieren. Relaisnummern beginnen bei 1; leer bedeutet kein Ausgang. Vorhandene Einstellungen werden beim Update erhalten. Der GPIO-Modus ist derzeit nur eine interne Simulation und schaltet keinen physischen GPIO.
