# TI Konnektor Patch

Jeder Konnektor [Link hier einfügen] der **Telematik Infrastruktur** (TI) enthält mehrere Smartcards auf denen Zertifikate gespeichert werden.
Aus Sicherheitsgründen haben diese Zertifikate ein Verfallsdatum, das heisst sie müssen regelmäßig erneut werden.
Nicht alle Hersteller*innen haben einen Mechanismus zur Verlängerung der Zertifikate implementert, nach auslaufen der Zertifikate muss also der gesamte Konnektor getauscht werden.
Aktuelle laufen die ersten Zertifikate aus. 

Die gematik, das für die TI verantwortkiche Unternehmen, hat sich entschieden alle Konnektoren entsprechen auszutauschen. Dies erzeugt Kosten im Bereich vom **300 bis 400 Millionen Euro**


Wir zeigen hier <u>kostenlos</u> eine Softwarelösung für das Problem, von der die Hersteller behaupten, dass sie unmöglich sei.

## Funktionsweise

Unser Patch klinkt sich in die Kommunkation zwischen der Software auf dem Konnektor und der SmartCard ein. Das geht, weil die Kommunikation zur SmartCard nicht abgesichert ist. Unter anderem deshalb war auch der [Angriff](https://twitter.com/fluepke/status/1576584063896256513) auf den "sicheren" Speicher im *Secunet* Adapter möglich.

Sowohl bei dem Produkt der *Secunet* als auch der *CompuGroup Medical* kommt die Software `pcscd` zur Kommunikation mit den SmartCards zum Einsatz. Diese Software öffnet ein Unix Socket (z.B. in `/var/run/pcscd.comm`) über das Anwendungen mit dem `pcscd` interagieren, um der SmartCard Befehle zu senden und Antworten von dieser zu empfangen.

Unser Lösungsvorschlag besteht darin, an der Stelle des ursprünglichen `pcscd` einen modifizierten `pcscd` zu starten, der alle Befehle an die SmartCard wie gewohnt weiterleitet. Wird jedoch der Befehl zum Auslesen eines der drei vom Auslaufen betroffenen Zertifikate gesendet, antwortet unser `pcscd` mit einem verlängerten Zertifikat aus dem Dateisystem.

Dadurch sind keine Veränderungen an der bestehenden Software der Hersteller notwendig. Es muss lediglich eine Teilkomponente des Linuxsystems, auf dem die Hersteller ihre TI Konnektoren basiert haben, umkonfiguriert bzw. ausgetauscht werden.

### Detaillierte Beschreibung

Wir verwenden einen handelsüblichen [`pcscd`](https://github.com/LudovicRousseau/PCSC) und simulieren diesem SmartCards mithilfe des Projekts [Virtual Smart Card](https://frankmorgner.github.io/vsmartcard/virtualsmartcard/README.html).

1. Der bestehene `pcscd` des Herstellers bleibt laufen, sein Socket wird aber an einen neuen Ort verschoben: `mv /var/run/pcscd.comm /var/run/old_pcscd.comm`
2. Es ist ein handelsüblicher `pcscd` sowie `virtualsmartcard` zu installieren und zu starten. Wichtig ist, dass der `pcscd` konfiguriert wird, lediglich die Treiber für `virtualsmartcard` zu laden. Siehe dazu bspw. `./reader.conf.d`
3. In dem Verzeichnis `./certs` sind die verlängerten Zertifikate mit folgenden Dateinamen zu hinterlegen:
    1. `AK_AUT.der`
    2. `NK_VPN.der`
    3. `SAK_AUT.der`
3. Es wird das `./save_400m_euro.py` Python Skript gestartet. Dieses verfolgt in der `execute()` Methode alle APDUs und prüft ob ein Zugriff auf die Zertifikatsdateien erfolgt. Per Environment wird dem Skript die Lokation des bisherigen `pcscd` mitgeteilt, damit eine Kommunikation zur echten SmartCard weiterhin möglich ist: `PCSCLITE_CSOCK_NAME=/var/run/old_pcscd.comm ./save_400m_euro.py`

## Installation

Die Hersteller müssen dieses Stück Software in eine Update-Datei verpacken, diese signieren und bereitstellen, denn schließlich darf nur Software vom Hersteller auf dem Konnektor ausgeführt werden.

Für die Verlängerung der Zertifikatslaufzeiten braucht es die *gematik*, denn die verantwortet die dazu notwendige Certificate Authority (CA).

## Forderungen

Wir fordern die gematik auf, ihre CA für die Verlängerung der Laufzeiten einzusetzen.
Wir fordern die Hersteller auf, die Laufzeitverlängerung umzusetzen statt die Ärzte mit absurden Preisen auszubeuten.
Wir fordern die Politik auf, die Hersteller endlich an die Leine zu nehmen und der Geldverbrennung in der TI ein Ende zu setzen.
Wir fordern das BSI auf, den Einsatz der geringen RSA Schlüssellänge von 2048 Bit in diesem Sonderfall auch über das Jahr 2025 zu erlauben, da es sich lediglich um die äußerste Sicherungsschicht (VPN) handelt. Innenliegende Kommunikation, die medizinische Daten trägt, ist zusätzlich mit TLS in einer modernen Konfiguration gesichert.
