# TI Konnektor Patch

Die **Telematik Infrastruktur** (TI) Konnektoren enthalten Smartcards, auf denen Zertifikate gespeichert sind.
Diese Zertifikate haben genau wie TLS Zertifikate aus Sicherheitsgründen ein Verfallsdatum.
Leider haben nicht alle Hersteller einen Mechanismus entwickelt, diese Zertifikate zu verlängern und stattdessen zu Lasten der Umwelt ein Produkt mit geplanter Obsoloszenz verkauft.

Nun hat sich die gematik, welche die TI verantwortet, zum Austausch der Konnektoren entschieden, was erhebliche **Kosten von 300 bis 400 Millionen Euro** erzeugt!

Wir zeigen hier <u>kostenlos</u> eine Softwarelösung für das Problem auf, von der die Hersteller behaupten, dass sie unmöglich sei.

## Funktionsweise

Unser Patch klinkt sich in die Kommunkation zwischen der Software auf dem Konnektor und der SmartCard ein. Das geht, weil die Kommunikation zur SmartCard nicht abgesichert ist. Unter anderem deshalb war auch der [Angriff](https://twitter.com/fluepke/status/1576584063896256513) auf den "sicheren" Speicher im *Secunet* Adapter möglich.

Sowohl bei dem Produkt der *Secunet* als auch der *CompuGroup Medical* kommt die Software `pcscd` zur Kommunikation mit den SmartCards zum Einsatz. Diese Software öffnet ein Unix Socket (z.B. in `/var/run/pcscd.comm`) über das Anwendungen mit dem `pcscd` interagieren, um der SmartCard Befehle zu senden und Antworten von dieser zu empfangen.

Unser Lösungsvorschlag besteht darin, an der Stelle des ursprünglichen `pcscd` einen modifizierten `pcscd` zu starten, der alle Befehle an die SmartCard wie gewohnt weiterleitet. Wird jedoch der Befehl zum Auslesen eines der drei vom Auslaufen betroffenen Zertifikate gesendet, antwortet unser `pcscd` mit einem verlängerten Zertifikat aus dem Dateisystem.

Dadurch sind keine Veränderungen an der bestehenden Software der Hersteller notwendig. Es muss lediglich eine Teilkomponente des Linuxsystems, auf dem die Hersteller ihre TI Konnektoren basiert haben, umkonfiguriert bzw. ausgetauscht werden.

### Detaillierte Beschreibung

Wir verwenden einen handelsüblichen [`pcscd`](https://github.com/LudovicRousseau/PCSC) und simulieren diesem SmartCards mithilfe des Projekts [Virtual Smart Card](https://frankmorgner.github.io/vsmartcard/virtualsmartcard/README.html).

1. Der bestehene `pcscd` des Herstellers bleibt laufen, sein Socket wird aber an einen neuen Ort verschoben: `mv /var/run/pcscd.comm /var/run/old_pcscd.comm`
2. Es ist ein handelsüblicher `pcscd` sowie `virtualsmartcard` zu installieren und zu starten. Wichtig ist, dass der `pcscd` konfiguriert wird, lediglich die Treiber für `virtualsmartcard` zu laden. Siehe dazu bspw. `./reader.conf.d`
3. In dem Verzeichnis `./renewed_certs` sind die verlängerten Zertifikate mit folgenden Dateinamen zu hinterlegen:
    1. `MF_DF.AK_EF.C.AK.AUT.R2048.der`
    2. `MF_DF.NK_EF.C.NK.VPN.R2048.der`
    3. `MF_DF.SAK.EF.C.SAK.AUT.R2048.der`
3. Es wird das `./save_400m_euro.py` Python Skript gestartet. Dieses verfolgt in der `execute()` Methode alle APDUs und prüft ob ein Zugriff auf die Zertifikatsdateien erfolgt. Per Environment wird dem Skript die Lokation des bisherigen `pcscd` mitgeteilt, damit eine Kommunikation zur echten SmartCard weiterhin möglich ist: `PCSCLITE_CSOCK_NAME=/var/run/old_pcscd.comm ./save_400m_euro.py`

## Installation

Die Hersteller müssen dieses Stück Software in eine Update-Datei verpacken, diese signieren und bereitstellen, denn schließlich darf nur Software vom Hersteller auf dem Konnektor ausgeführt werden.

Für die Verlängerung der Zertifikatslaufzeiten braucht es die *gematik*, denn die verantwortet die dazu notwendige Certificate Authority (CA).

## Forderungen

Wir fordern die gematik auf, ihre CA für die Verlängerung der Laufzeiten einzusetzen.
Wir fordern die Hersteller auf, die Laufzeitverlängerung umzusetzen statt die Ärzte mit absurden Preisen auszubeuten.
Wir fordern die Politik auf, die Hersteller endlich an die Leine zu nehmen und der Geldverbrennung in der TI ein Ende zu setzen.
Wir fordern das BSI auf, den Einsatz der geringen RSA Schlüssellänge von 2048 Bit in diesem Sonderfall auch über das Jahr 2025 zu erlauben, da es sich lediglich um die äußerste Sicherungsschicht (VPN) handelt. Innenliegende Kommunikation, die medizinische Daten trägt, ist zusätzlich mit TLS in einer modernen Konfiguration gesichert.
