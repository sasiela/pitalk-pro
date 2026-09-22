# Architektura i sprzęt

## Platforma odniesienia

Raspberry Pi 3 Model B Rev 1.2, Debian GNU/Linux 13 (trixie), aarch64. W czasie diagnozy system podawał Debian 13.6 i kernel 6.18.39+rpt-rpi-v8. Wyświetlacz Adafruit PiTFT 2.2 cala, 240×320, nakładka `pitft22`. Ekran jest rysowany przez Pillow i zapisywany do `/dev/fb0` jako RGB565. Czcionki DejaVu są zależnością systemową. To nie aplikacja desktopowa ani strona na samym ekranie PiTFT.

| GPIO BCM | Funkcja |
| --- | --- |
| 17 | BACK |
| 22 | UP |
| 23 | DOWN |
| 27 | ENTER |
| 26 | Przytrzymywany przycisk PTT, wejście z pull-up, aktywne zero |
| 24 | Programowy sygnał otwarcia squelcha; w tym jądrze sysfs `gpio536` |

Nie traktuj liczby 536 jako uniwersalnego numeru GPIO. Wynika z mapowania konkretnego systemu. Przycisk PTT był testowany z eliminacją drgań 30 ms; bez niej rejestrował serię krótkich zboczy.

## Warstwy

- `/usr/local/bin/sqlink-screen.py`: główny ekran i menu, przyciski, renderowanie, TG i wskaźniki.
- `/usr/lib/sqlink/`: kontroler, API SQLink, stan reflektora, GPIO, audio, motywy i edytory poszczególnych menu.
- `/usr/local/bin/sqlink-ptt-button.py`: oddzielny proces przycisku, debounce 30 ms, uzbrojenie dopiero po puszczeniu przycisku, watchdog i zwolnienie PTT przy wyjściu.
- `/usr/local/sbin/sqlink-gpio-setup.sh`: eksport GPIO24/sysfs, atomowe ustawienie stanu idle HIGH, prawa do sterowania dla aplikacji.
- `svxlink.service`: silnik głosu i połączenie z reflektorem. Konfiguracja zawiera SimplexLogic i ReflectorLogic połączone przez ReflectorLink.
- Uprzywilejowane helpery Wi-Fi oraz Bluetooth: wykonują ograniczone operacje systemowe za pośrednictwem lokalnych socketów Unix.
- `/opt/sqlink-web/server.py` i `static/`: lokalny panel WWW. Korzysta z tych samych modułów i helperów co ekran.

## PTT i audio

GPIO26 → proces PTT → `sqlink.gpio` → GPIO24 w stanie LOW → `Rx1` z `SQL_DET=GPIO` i `GPIO_SQL_PIN=!gpio536` → audio mikrofonu do SvxLink/reflektora. W konfiguracji prototypu `Tx1` ma `PTT_TYPE=NONE`. Jest to sterowanie lokalnym wejściem głosowym do sieci; nie oznacza gotowego interfejsu PTT zewnętrznego radiotelefonu.

SvxLink używa `AUDIO_DEV=alsa:pipewire`. PipeWire, warstwa zgodna z PulseAudio i WirePlumber pracują w sesji konta `sqlink`. UID 1002 jest wpisany w kilka usług i ścieżek `/run/user/1002`. Wybór USB/Bluetooth oraz głośność opierają się na `pactl` i helperze Bluetooth. Profile Bluetooth mają znaczenie dla wejścia mikrofonowego i jakości dźwięku; nie zakładaj, że każdy profil zapewnia równocześnie to samo wejście i wyjście.

## Stan TG i nadawcy

`/usr/share/svxlink/events.d/local/RadioStatus.tcl` opakowuje zdarzenia ReflectorLogic (`tg_selected`, `talker_start`, `talker_stop`). Zapisuje atomowo `/dev/shm/sqlink-radio-state`: PID, TG, flaga odbioru i callsign. Czytelnicy porównują PID z `/run/svxlink.pid`, aby odrzucić stan sprzed restartu.

- MONITOR: brak aktywnego RX/TX przy gotowości do nasłuchu.
- RX: aktualnie odbierana transmisja; wyświetlany jest callsign i pasek audio.
- TX: aktywny lokalny PTT. Nie jest to dowód, że mikrofon faktycznie dostarcza sygnał lub że transmisja dotarła do serwera.
- ONLINE/OFFLINE: rzeczywisty lokalny stan połączenia SvxLink. API statusu serwera daje informacje dodatkowe.

`radio_status.py` pobiera próbki przez `parec` w osobnym wątku; szybsze rysowanie miernika nie powinno wymuszać kosztownych zapytań sieciowych przy każdej klatce.

## Panel WWW

HTTPS na porcie 8443, Python HTTP server i statyczny HTML/CSS/JS. Ekrany: Overview, Talk groups, Audio, Bluetooth, Wi-Fi, User, System. Logowanie jako systemowy użytkownik `sqlink` przez PAM (`/etc/pam.d/sqlink-web`, helper `sqlink_web_auth.py`). To nie hasło do reflektora. Sesje są trzymane w pamięci, dlatego restart panelu może wymagać ponownego logowania. Operacje używają tokenu CSRF; panel ma filtr klienta LAN i nagłówka Host.

Talk groups pokazuje aktywność, wybraną TG i listy stacji. „Connected” oznacza aktualnie wybraną TG według danych serwera. „Monitoring” oznacza skonfigurowaną listę monitorowania, nie gwarancję aktywnego odbioru w tej chwili. Kliknięcie callsign otwiera szczegóły stacji z dostępnych danych API, nie zdalną konfigurację administracyjną tej stacji.

Odsłuch: `/api/listen` → `listen_audio.py` → monitor bieżącego wyjścia PulseAudio (`<sink>.monitor`) → PCM s16le/16 kHz/mono → AudioWorklet przeglądarki. Maksymalnie cztery strumienie. Poza RX wysyłana jest cisza. Strumień nie zapisuje nagrania i nie zabiera dźwięku urządzeniu. Głośność przeglądarki jest osobna. Zmiana domyślnego wyjścia jest wykrywana podczas odsłuchu. Zamknięcie Overview, Stop lub wylogowanie zatrzymuje odsłuch.

Pułapka: `ProtectHome=yes` w usłudze ukrywa `/run/user`. Działający prototyp używa bind mount socketu PulseAudio do `/run/sqlink-web-audio` i zmiennej `PULSE_SERVER`. Obraz alpha ma inny wariant: bind całego runtime użytkownika z zależnością od `user@1002.service`. Nie mieszaj tych wariantów bez sprawdzenia startu usług.

## Testy audio WWW

`audio_test.py` obsługuje jedno ograniczone czasowo zadanie należące do sesji. Paplay odtwarza wygenerowany ton, parec odczytuje domyślny mikrofon i oblicza poziom bez zapisu nagrania. GET/POST `/api/audio-test`; frontend odpytuje stan co 250 ms. Test nie steruje GPIO; odczytuje stan radia i przerywa przy RX/PTT. [Instrukcja i sprawdzenia](../build/AUDIO-TESTS.md).

## Profile reflektorów (22 września 2026)

`sqlink_profiles.py` zastępuje bezpośrednią edycję konta w User. Root przechowuje bazę prywatną i publikuje metadane aktywnego profilu do `profile_state.py`. UI PiTFT i `/api/profiles` korzystają ze wspólnego helpera. API nazw i stacji jest ograniczone do dostawcy danego profilu; None nie odpytuje SQLink. Usługa `sqlink-profiles.service` przygotowuje konfigurację domyślnego profilu na rozruch. [Pełny opis](../build/PROFILES.md).
