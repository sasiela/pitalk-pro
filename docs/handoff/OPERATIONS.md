# Obsługa, konfiguracja i dalszy rozwój

## Istotne lokalizacje na urządzeniu

| Lokalizacja | Znaczenie |
| --- | --- |
| `/etc/svxlink/svxlink.conf` | Callsign, hasło reflektora, TG, audio i logika; plik prywatny |
| `/var/backups/sqlink-user/` | Kopie konfiguracji użytkownika, mogą zawierać hasła |
| `/etc/NetworkManager/system-connections/` | Zapisane Wi-Fi, właściciel root, pliki 600 |
| `/var/lib/sqlink-display/settings.json` | Kolory, jasność i timeout menu |
| `/var/lib/sqlink-bluetooth/preferences.json` | Preferencje Bluetooth |
| `/var/lib/bluetooth/` | Systemowe parowania; nie eksportować |
| `/run/sqlink-wifi/control.sock` | Helper Wi-Fi i konfiguracji użytkownika |
| `/run/sqlink-bluetooth/control.sock` | Helper Bluetooth i audio |
| `/run/user/1002/pulse/native` | Socket zgodności PulseAudio dla sesji sqlink |
| `/dev/shm/sqlink-radio-state` | Bieżąca TG / RX / callsign; dane nietrwałe |
| `/var/log/svxlink` | Log SvxLink |
| `/etc/sqlink-web/cert.pem`, `key.pem` | Certyfikat HTTPS i prywatny klucz |
| `/etc/pam.d/sqlink-web` | Uwierzytelnianie panelu kontem systemowym |

Hasło systemowe i hasło reflektora są niezależne. Panel używa konta systemowego `sqlink`. Hasło reflektora pozostaje w chronionym pliku SvxLink; UI nie powinien zwracać go klientowi. Zapis przez helper tworzy kopię i stosuje konfigurację. Nie używaj `cat` na aktywnej konfiguracji do diagnostyki wymagającej tylko jednego niesekretnego pola.

## Zależności

System Linux ARM64 z systemd, SvxLink, NetworkManager (`nmcli`), BlueZ, PipeWire z kompatybilnością PulseAudio, WirePlumber, narzędzia `pactl`/`parec`, Python 3, Pillow, lgpio, bindings D-Bus/GLib używane przez helper Bluetooth, czcionki DejaVu i Avahi dla `.local`. To zestaw zależności funkcjonalnych; repozytorium nie ma jeszcze zamkniętej listy wersji ani w pełni automatycznego instalatora od czystego OS.

Konto `sqlink` ma UID/GID 1002 w prototypie i dodatkowe grupy audio/gpio/video. Usługi odwołują się do sesji użytkownika. Konfiguracja headless WirePlumber wyłącza seat-monitoring dla Bluetooth. Dołączony przykład odtwarza tę poprawkę; nie jest eksportem katalogu domowego ani tokenów audio.

## Diagnostyka

Najpierw odczyty, potem zmiany. Sprawdzaj status usług, krótki wycinek logu, stan interfejsów i aktualny domyślny sink/source. Zanonimizuj logi przed dodaniem do repozytorium.

Przykłady odczytów na Pi:

```sh
systemctl is-active svxlink sqlink-screen sqlink-web sqlink-ptt-button
nmcli device status
ip -br addr
hostnamectl --static
```

Polecenia `pactl` wykonuj w sesji `sqlink`, z właściwym `XDG_RUNTIME_DIR`. Wynik w sesji root bez środowiska audio może być mylący. W przypadku problemów z odsłuchem sprawdź także `PULSE_SERVER` i bind mount z drop-in usługi WWW.

Gdy panel odmawia wejścia po zmianie nazwy/IP, sprawdź `local_access()` w `server.py`, mDNS/Avahi oraz certyfikat. Samo `hostnamectl` nie aktualizuje wszystkich list dozwolonych hostów aplikacji.

## Małe wdrożenie na istniejący prototyp

1. Ustal zakres zmiany i odczytaj aktualne pliki urządzenia; snapshot może być starszy.
2. Zapisz kopię tylko plików objętych zmianą, z uprawnieniami chroniącymi konfigurację.
3. Zmodyfikuj i sprawdź składnię lokalnie; nie importuj bezpośrednio modułów uruchamiających sprzęt.
4. Przenieś wybrane pliki, zachowując właścicieli i tryby. Nie kopiuj szablonów nad aktywne hasła/Wi-Fi.
5. Restartuj wyłącznie potrzebną usługę. Po zmianie unitów wykonaj daemon-reload. Restart serwera WWW unieważnia jego sesje w pamięci i zatrzymuje odsłuch.
6. Zweryfikuj usługę, log i konkretny przepływ. Przy błędzie przywróć kopię, restartuj tę samą usługę i ponownie sprawdź.

Nie ma tu polecenia „wdroż wszystko”, bo mogłoby nadpisać konfigurację lub zablokować dostęp. Zlecone zmiany można wdrażać samodzielnie po sprawdzeniu tych zależności.

## Lokalne kontrole

`software/check-source.py` sprawdza składnię Pythona bez uruchamiania sprzętu oraz prosty filtr sekretów. JavaScript można sprawdzić `node --check` dla każdego pliku `.js`. Skrypty shell — `bash -n`. To kontrole statyczne, nie dowód poprawnego działania GPIO, audio, sieci czy rozruchu.

Symulacja `software/image-tools/test-firstboot.py` używa plików tymczasowych i zastępuje polecenia systemowe. Nie uruchamiaj samego `firstboot.py` ani `sanitize.py` na systemie roboczym. Są przeznaczone dla przygotowanego środowiska obrazu.
