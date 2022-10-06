# TI Konnektor Patch

Jeder Konnektor [Link hier einfügen] der **Telematik Infrastruktur** (TI) enthält mehrere SmartCards, auf denen Zertifikate gespeichert werden.
Aus Sicherheitsgründen haben diese Zertifikate ein Verfallsdatum, das heißt sie müssen regelmäßig erneut werden.
Nicht alle Hersteller*innen haben einen Mechanismus zur Verlängerung der Zertifikate implementert, nach Auslaufen der Zertifikate muss also der gesamte Konnektor getauscht werden.
Aktuelle laufen die ersten Zertifikate aus. 

Die gematik, das für die TI verantwortliche Unternehmen, hat sich entschieden, alle Konnektoren entsprechen auszutauschen. Dies erzeugt Kosten im Bereich vom **300 bis 400 Millionen Euro**.


Wir zeigen hier eine <u>kostenlose</u> Softwarelösung für das Problem, von der die Hersteller behaupten, dass sie unmöglich sei.

## Funktionsweise

Unser Patch klinkt sich in die Kommunkation zwischen der Software auf dem Konnektor und der SmartCard ein. Das geht, weil die Kommunikation zur SmartCard nicht abgesichert ist. Unter anderem deshalb war auch der [Angriff auf den "sicheren" Speicher](https://twitter.com/fluepke/status/1576584063896256513) im *Secunet* Adapter möglich.

Sowohl bei dem Produkt der *Secunet* als auch der *CompuGroup Medical* kommt die Software `pcscd` zur Kommunikation mit den SmartCards zum Einsatz. Diese Software öffnet einen [Unix Domain Socket](https://de.wikipedia.org/wiki/Unix_Domain_Socket) (z. B. in `/var/run/pcscd.comm`), über den Anwendungen mit dem `pcscd` interagieren, um der SmartCard Befehle zu senden und Antworten von dieser zu empfangen.

Unser Referenzimplementierung für die Verlängerung der Zertifikatslaufzeiten besteht darin, an der Stelle des ursprünglichen `pcscd` einen modifizierte Version zu starten, die alle Befehle an die SmartCard wie gewohnt weiterleitet. Wird jedoch der Befehl zum Auslesen eines der drei vom Auslaufen betroffenen Zertifikate gesendet, antwortet unser `pcscd` mit einem verlängerten Zertifikat aus dem Dateisystem.

Dadurch sind keine Veränderungen an der bestehenden Software der Hersteller notwendig. Es muss lediglich eine Teilkomponente des Linux-Systems, auf dem die Hersteller ihre TI Konnektoren basiert haben, umkonfiguriert bzw. ausgetauscht werden.

### Detaillierte Beschreibung

Wir verwenden einen handelsüblichen [`pcscd`](https://github.com/LudovicRousseau/PCSC) und simulieren diesem SmartCards mithilfe des Projekts [Virtual Smart Card](https://frankmorgner.github.io/vsmartcard/virtualsmartcard/README.html).

1. Auf dem Konnektor bleibt der bestehende `pcscd` des Herstellers im Hintergrund aktiv, sein Socket wird aber an einen neuen Ort im Dateisystem verschoben: `mv /var/run/pcscd.comm /var/run/old_pcscd.comm`
2. Dann wird ein handelsüblicher `pcscd` sowie `virtualsmartcard` installiert und gestartet. Wichtig ist, dass der `pcscd` konfiguriert wird, lediglich die Treiber für `virtualsmartcard` zu laden. Siehe dazu bspw. `./reader.conf.d`
3. In dem Verzeichnis `./certs` sind die verlängerten Zertifikate mit folgenden Dateinamen zu hinterlegen:
    1. `AK_AUT.der`
    2. `NK_VPN.der`
    3. `SAK_AUT.der`
4. Zuletzt muss das Python-Skript `./save_400m_euro.py` aus diesem Projekt gestartet werden. Dieses verfolgt in der `execute()` Methode alle APDUs und prüft, ob ein Zugriff auf die Zertifikatsdateien erfolgt.

## Installation

Die Hersteller müssen dieses Stück Software in eine Update-Datei verpacken, diese signieren und bereitstellen, denn schließlich darf nur Software vom Hersteller auf dem Konnektor ausgeführt werden.

Für die Verlängerung der Zertifikatslaufzeiten braucht es die *gematik*, denn sie verantwortet und betreibt die dazu notwendige Certificate Authority (CA).

## Forderungen

Wir fordern die gematik auf, ihre CA für die Verlängerung der Laufzeiten einzusetzen.
Wir fordern die Hersteller auf, die Laufzeitverlängerung umzusetzen, statt das Gesundheitssystem durch die aufgerufenen astronomischen Preisen auszubeuten.
Wir fordern die Bundesgesundheitsministerium auf, die Hersteller endlich an die Leine zu nehmen und der Geldverbrennung in der TI ein Ende zu setzen.
Wir fordern das Umweltministerium auf, die allein schon aus Nachhaltigkeitsgesichtspunkten völlig sinnlose tausendfache Vernichtung einsatzfähiger Hardware zu verhindern.
Wir fordern das BSI auf, den Einsatz der geringen Schlüssellänge von 2048 Bit für den verwendeten RSA-Algorithmus in diesem Sonderfall auch über das Jahr 2025 zu erlauben, da es sich lediglich um die äußere Sicherungsschicht (VPN) handelt. Innenliegende Kommunikation, die medizinische Daten trägt, ist zusätzlich mit TLS in einer modernen Konfiguration gesichert.
