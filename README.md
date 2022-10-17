# TI Konnektor Patch

Jeder [Konnektor](https://fachportal.gematik.de/hersteller-anbieter/komponenten-dienste/konnektor), der zum Zugriff auf die **Telematik Infrastruktur** (TI) der *gematik* benötigt wird, enthält mehrere Smartcards, auf denen Zertifikate gespeichert werden.
Aus Sicherheitsgründen haben diese Zertifikate ein Verfallsdatum. Daher müssen sie regelmäßig erneut werden.
Nicht alle Hersteller*innen haben einen Mechanismus zur Verlängerung der Zertifikate implementert. Nach Auslaufen der Zertifikate muss also der gesamte Konnektor getauscht werden.
Derzeit laufen die ersten Zertifikate aus. 

Verantwortlich für die TI ist die gematik. Deren Gesellschafter [haben entschieden](https://www.gematik.de/newsroom/news-detail/aktuelles-erste-konnektoren-laufen-im-september-aus), diese Konnektoren auszutauschen. Das erzeugt Kosten im Bereich vom **300 bis 400 Millionen Euro**.

Wir zeigen hier eine **kostenlose** Softwarelösung für das Problem, von der die Hersteller*innen behaupten, dass sie unmöglich sei.

## Funktionsweise

Unser Patch klinkt sich in die Kommunkation zwischen der Software auf dem Konnektor und der Smartcard ein. Das geht, weil die Kommunikation zur Smartcard nicht abgesichert ist. Unter anderem deshalb war auch der [Angriff auf den "sicheren" Speicher](https://twitter.com/fluepke/status/1576584063896256513) im *Secunet* Adapter möglich.

> **Wichtig**: Unser Patch stellt keinen Angriff auf die Integrität des Konnektors dar. Zwar klinkt sich der Patch in die Kommunikation zur Smartcard ein, es werden aber nur öffentliche, also nicht geheime Daten verändert. Die privaten Schlüssel verbleiben unverändert auf der besonders abgesicherten Smartcard.

Sowohl bei dem Produkt der *Secunet* als auch bei der *CompuGroup Medical* kommt die Software *PC/SC Smart Card Daemon* ([`pcscd`](https://github.com/LudovicRousseau/PCSC)) zur Kommunikation mit den SmartCards zum Einsatz. Diese Software öffnet einen [Unix Domain Socket](https://de.wikipedia.org/wiki/Unix_Domain_Socket) (z. B. in `/var/run/pcscd.comm`), über den Anwendungen mit dem `pcscd` interagieren, um der Smartcard Befehle zu senden und Antworten von dieser zu empfangen.

Unsere Referenzimplementierung für die Verlängerung der Zertifikatslaufzeiten besteht darin, an der Stelle des ursprünglichen `pcscd` eine modifizierte Version zu starten, die alle Befehle an die SmartCard wie gewohnt weiterleitet. Wird jedoch der Befehl zum Auslesen eines der drei vom Auslaufen betroffenen Zertifikate gesendet, antwortet unser `pcscd` mit einem verlängerten Zertifikat aus dem Dateisystem.

Dadurch sind keine Veränderungen an der bestehenden Software der Hersteller notwendig. Es muss lediglich eine Teilkomponente des Linux-Systems, auf dem die Hersteller ihre TI Konnektoren basiert haben, umkonfiguriert bzw. ausgetauscht werden.

### Detaillierte Beschreibung

Wir verwenden einen handelsüblichen *PC/SC Smart Card Daemon* ([`pcscd`](https://github.com/LudovicRousseau/PCSC)) und simulieren diesem SmartCards mithilfe des Projekts [Virtual Smart Card](https://frankmorgner.github.io/vsmartcard/virtualsmartcard/README.html).

1. Auf dem Konnektor bleibt der bestehende `pcscd` des Herstellers im Hintergrund aktiv, sein Socket wird aber an einen neuen Ort im Dateisystem verschoben: `mv /var/run/pcscd.comm /var/run/old_pcscd.comm`
2. Dann wird ein handelsüblicher `pcscd` sowie `virtualsmartcard` installiert und gestartet. Wichtig ist, dass der `pcscd` so konfiguriert wird, lediglich die Treiber für `virtualsmartcard` zu laden.
3. In dem Verzeichnis `./certs` sind die verlängerten Zertifikate mit folgenden Dateinamen zu hinterlegen:
    1. `AK_AUT.der`
    2. `NK_VPN.der`
    3. `SAK_AUT.der`
4. Zuletzt muss das Python-Skript `./save_400m_euro.py` aus diesem Projekt gestartet werden. Dieses verfolgt in der `execute()` Methode alle APDUs und prüft, ob ein Zugriff auf die Zertifikatsdateien erfolgt.

## Installation

Die Hersteller müssen dieses Skript in eine Update-Datei verpacken, diese signieren und bereitstellen, denn schließlich darf nur Software vom Hersteller auf dem Konnektor ausgeführt werden.

Für die Verlängerung der Zertifikatslaufzeiten braucht es die *gematik*, denn sie verantwortet und betreibt die dazu notwendige Certificate Authority (CA).

## Forderungen

- Wir fordern die **gematik** auf, ihre CA für die Verlängerung der Laufzeiten einzusetzen.
- Wir fordern **alle Hersteller** ([CompuGroup Medical](https://www.cgm.com/deu_de), [secunet](https://www.secunet.com/), [RISE](https://www.rise-konnektor.de/)) auf, die Laufzeitverlängerung umzusetzen, statt das Gesundheitssystem durch die aufgerufenen astronomischen Preise auszubeuten.
- Wir fordern das **[Bundesgesundheitsministerium](https://www.bundesgesundheitsministerium.de/service/kontakt.html)** auf, die Hersteller endlich an die Leine zu nehmen und der Geldverbrennung in der TI ein Ende zu setzen.
- Wir fordern das **[Umweltministerium](https://www.bmuv.de/service/buergerservice/kontaktformular-fuer-ihre-fragen)** auf, die allein schon aus Nachhaltigkeitsgesichtspunkten völlig sinnlose tausendfache Vernichtung einsatzfähiger Hardware zu verhindern.

## Mitmachen

Meldet euch beim **[Bundesgesundheitsministerium](https://www.bundesgesundheitsministerium.de/service/kontakt.html)**, **[Umweltministerium](https://www.bmuv.de/service/buergerservice/kontaktformular-fuer-ihre-fragen)** und bei eurem lokalen [Abgeordneten](https://www.abgeordnetenwatch.de/) und verdeutlicht, dass ihr die obigen [Forderungen](#forderungen) unterstützt.
