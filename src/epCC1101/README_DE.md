# epCC1101

## Allgemeines

Der CC1101 ist ein kostengünstiger und energieeffizienter RF-Transceiver von Texas Instruments. Er unterstützt verschiedene Frequenzbänder (u. a. 315 MHz, 433 MHz, 868 MHz, 915 MHz), mehrere Modulationsverfahren und flexible Konfigurationsmöglichkeiten.

Wesentliche Eigenschaften:
- Geringer Stromverbrauch im Empfangs- und Sende-Modus
- Unterstützte Frequenzbänder: 300–348 MHz, 387–464 MHz, 779–928 MHz
- Programmierbare Datenrate: bis zu 500 kBaud (abhängig von Modulation und Filtereinstellungen)
- Mehrere Modulationsmodi (2-FSK, GFSK, ASK/OOK, 4-FSK, MSK)
- Interne Paketverarbeitung (Preamble, Sync Word, Adressenprüfung, CRC-Checksum)
- Konfigurierbar über SPI-Schnittstelle

Projektziel:

In diesem Repository werden Funktionen und Beispiele bereitgestellt, um den CC1101 mithilfe einer gängigen Plattform (z. B. Arduino, ESP32 oder andere MCU) zu steuern. Die Bibliothek abstrahiert SPI-Registerzugriffe und bietet komfortable Methoden, um die Funkkommunikation schnell einzurichten.

## Verwendung

### Hardware-Verkabelung

Der CC1101 wird über eine SPI-Schnittstelle mit dem Mikrocontroller verbunden. Typisch sind folgende Pins belegt:
- MOSI (Master Out Slave In)
- MISO (Master In Slave Out)
- SCK (SPI Clock)
- CSN (Chip Select)
- Zusätzlich gegebenenfalls GDO0 bzw. GDO2 für Interrupt- oder Statussignale.

### Software Initialisierung

Nach dem Einbinden der Bibliothek werden die SPI-Schnittstelle und die CC1101-spezifischen Register initialisiert.
Es können vorkonfigurierte Register-Sätze (SmartRF Studio von TI oder eigene Settings) genutzt werden, um das Funkmodul für die gewünschte Frequenz, Datenrate und Modulation zu konfigurieren.

```python
from epCC1101 import Cc1101, Driver, presets
driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)
cc1101 = Cc1101(driver=driver)
cc1101.reset()
```

## Packet Format

Der CC1101 ermöglicht eine flexible Gestaltung der Pakete. Die Formate lassen sich grob in Packet Mode, Synchronous Serial Mode und Asynchronous Serial Mode einteilen.

### Packet Mode

Im Packet Mode übernimmt der CC1101 automatisch das Generieren von Preamble, Sync Word, CRC und ggf. Addressing. Auch das Empfangen und Prüfen dieser Felder erfolgt größtenteils im Hintergrund. Hierfür werden die RX- und TX-FIFOs genutzt.

#### Packet Structure

Die typische Struktur eines Pakets im Packet Mode sieht folgendermaßen aus:

| Block     | Optional | Länge       | Bedeutung |
|-----------|----------|-------------|-----------|
| Preamble  | Nein     | 2 - 24 Bytes| Dient der Empfängersynchronisation (Bit Sync) |
| Sync Word | Nein     | 2 Bytes     | Markiert den Anfang des gültigen Datenpakets (Byte Sync) |
| Length    | Ja       | 1 Byte      | Legt die Länge des zu empfangenden Nutzdatenbereichs fest (sofern nicht Fixed/Infinite-Length) |
| Address   | Ja       | 1 Byte      | Kann zur Adressierung eingesetzt werden |
| Payload   | Nein     |             | Nutzdaten |
| CRC       | Ja       | 1 Byte      | Prüfsumme zur Fehlererkennung |

#### Synchronous Serial Mode

Im Synchronous Serial Mode empfängt oder sendet man Daten seriell bitweise über GDOx-Pins, während der CC1101 als Frequenzsynthesizer und Modulator/Demodulator dient. Man hat also eine synchrone Taktleitung (meist über GDO), über die Bits getaktet werden.

Vorteile:
- Manuelle Kontrolle über Datenstrom.
-  Geeignet für Systeme, die eigene Paketbildung implementieren wollen.

Nachteile:
- Höhere Software-Komplexität, da die komplette Paketbildung (Preamble, Sync, CRC) manuell durchgeführt werden muss.

#### Asynchrouns Serial Mode

Im Asynchronous Serial Mode gibt der CC1101 die modulierten Daten auf einer der GDOx-Leitungen als kontinuierlichen Datenstrom aus bzw. empfängt diese darüber (in FM-Modi). Dies ähnelt einer UART-ähnlichen Kommunikation, jedoch ohne Taktleitung.

Vorteile:
- Kann z. B. für einfache OOK/ASK-Anwendungen genutzt werden.
- Schnelle Integration in bestehende serielle Protokolle.

Nachteile:
- Synchronisation und Paketbildung liegen komplett in der Verantwortung des Anwenders.

## Frequenzeinstellungen

Im Folgenden werden die Frequenzeinstellungen beschrieben.

### Base Frequency

Die Basisfreuqenz ist die Frequenz des Trägersignals und muss im Bereich 300–348 MHz, 387–464 MHz oder 779–928 MHz liegen.

### Frequency Deviation

Die Frequenzabweichung beschreibt die Abweichung für FSK-Modulation. Eine größere Abweichung erhöht die Signalbandbreite, kann aber die Störfestigkeit verbessern.

### Receiver Bandwidth

Die Bandbreite des Empfängers. Ein engerer Filter reduziert Rauschen, kann aber zu Datenverlusten führen, wenn die Abweichung oder das Frequenz-Offset zu groß wird.

### Channel Spacing

Bei Nutzung mehrerer Channels beschreibt das Channel Spacing den Abstand zwischen den einzelnen Channels. 

## Modulation Formats

Der CC1101 beherrscht verschiedene Modulationsformen. Mögliche Einstellungen sind:

- 0x00: 2-FSK
- 0x01: GFSK
- 0x03: ASK/OOK
- 0x04: 4-FSK
- 0x07: MSK

### 2-FSK - Frequency Shift Keying 

- Frequency Shift Keying mit zwei Frequenzzuständen (Mark/Space).
- Einfach zu implementieren und robust.
- Gute Reichweiten bei niedrigen Baudraten.

### GFSK - Gaussian Frequency Shift Keying 

- Ist eine geglättete Variante von FSK.
- Reduziert Nebenausstrahlungen und erhöht die spektrale Effizienz.

### ASK/OOK - Amplitude Shift Keying / On-Off Keying

- Besonders geeignet für sehr einfache Protokolle (z. B. Fernbedienungen, Türklingeln).
- Stromsparend, da im “Off”-Zustand nur sehr wenig Leistung gesendet wird.

### 4-FSK

- Erweiterung von 2-FSK, nun mit vier Frequenzzuständen.
- Ermöglicht höhere Datenraten auf gleichem Frequenzband, jedoch auf Kosten höherer Komplexität.

### MSK - Minimum Shift Keying

- Spezielle FSK-Variante mit minimaler Frequenzabweichung.
- Kontinuierliche Phasenübergänge sorgen für besonders effiziente Spektrumnutzung.

