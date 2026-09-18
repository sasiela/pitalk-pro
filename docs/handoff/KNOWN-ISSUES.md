# Ograniczenia i nierozstrzygnięte sprawy

## Potwierdzone podczas wcześniejszych prac

- Wi-Fi przestało działać, gdy NetworkManager nie miał zapisanego profilu. Po utworzeniu profilu połączenie działało, autoconnect był włączony, interfejs wlan0 i DHCP poprawne. Przyczyny wcześniejszego zniknięcia profilu nie ustalono — nie przedstawiaj domysłu jako faktu.
- Surowy przycisk PTT dawał serię krótkich zboczy; debounce 30 ms dał czytelne pary wciśnięcie/puszczenie.
- Powtarzany komunikat Bluetooth „connected to device” analizowano i dodano konfigurację WirePlumber dla pracy bez sesji graficznej. Właściciel potwierdził poprawę. Zachowaj ją przy odtwarzaniu systemu.
- Odsłuch WWW zgłaszał brak wyjścia audio z powodu izolacji `/run/user` przez systemd. Dodano jawny bind socketu i `PULSE_SERVER`.
- Występowały rozłączenia reflektora z timeoutem heartbeat przy działającej sieci. Zaobserwowano automatyczne ponowne łączenie. Nie wykazano definitywnego usunięcia przyczyny po stronie całej ścieżki sieci/serwera. Potencjalny drugi klient używający tych samych danych rozważano, ale nie należy zakładać, że wyjaśnia każdy przypadek OFFLINE.
- Rotacja logu SvxLink wymagała poprawnych właścicieli oraz HUP; dołączono aktualny plik logrotate.

## Ograniczenia kodu/prototypu

- Prywatny filtr LAN/Host jest wpisany w kod panelu. W eksporcie zastąpiony przykładem. To istotny punkt przy wdrożeniu na innym routerze.
- UID/GID 1002 i gpio536 są zależnościami konkretnej instalacji.
- „Brightness” jest programowym przyciemnieniem renderowanego obrazu (LUT Pillow), a nie potwierdzonym sterowaniem mocą podświetlenia/PWM.
- Wygląd UI, przepływy menu i strumienie audio nie mają kompletnego automatycznego pokrycia testami. Składnia nie zastępuje testu na sprzęcie.
- Monitorowanie wielu TG nie jest mikserem równoczesnych rozmów. Trzeba odróżniać skonfigurowaną listę, aktualnie wybraną TG i to, co jest faktycznie odbierane.
- Pasek audio pokazuje poziom lokalnych próbek. Nie jest skalibrowanym miernikiem RF ani potwierdzeniem odbioru przez innych.
- BT zależy od dostępności urządzenia, profilu i domyślnego sink/source; sprawdź rzeczywisty sprzęt po zmianie routingu.
- Certyfikat panelu jest samopodpisany. `.local` wymaga mDNS; gdy nie działa, używa się adresu IP. Sam hostname nie zapewnia dostępu między odseparowanymi sieciami.
- Pole „config stacji” w popupie pokazuje dane udostępnione przez API reflektora, nie daje uprawnień do zmiany obcego urządzenia.

## Obraz alpha i publikacja

Obraz 6 GiB ma poprawne systemy plików i przeszedł kontrole statyczne, ale nie był uruchomiony z nowej karty. Wymaga testów: rozruch, pierwsza konfiguracja, powiększenie partycji, kolejność usług, ekran, PTT, USB, BT, Wi-Fi, WWW i audio. Zbudowano go z plików pobranych z pracującego Pi, nie z zatrzymanej migawki.

Pierwsza konfiguracja używa pliku na partycji FAT. Po użyciu jest nadpisywany i usuwany; nie traktuj tego jako gwarantowanego fizycznego wymazania pamięci flash. Nigdy nie publikuj obrazu po skonfigurowaniu go własnymi hasłami.

Przed publicznym wydaniem pozostają: instalator/powtarzalny build, pełne testy sprzętowe, przegląd licencji i źródeł zależności, instrukcja recovery oraz przegląd bezpieczeństwa panelu/helperów. Nie ustalono gotowej licencji całego oprogramowania w tej sesji; nie wymyślaj jej.

## Sensowna kolejność dalszych prac

1. Test alpha na zapasowej karcie, bez nadpisania działającej instalacji.
2. Usunięcie stałych IP/UID/mapowania GPIO przez konfigurację i wykrywanie.
3. Uporządkowany instalator i testy najważniejszych stanów PTT/TG/audio.
4. Diagnostyka heartbeat oparta na dłuższej obserwacji, jeżeli problem powróci.
5. Przygotowanie wersji do dystrybucji po testach i przeglądzie materiałów.

## Dopasowanie wejścia Bluetooth — poprawka 17 września 2026

PipeWire może nazwać wyjście `bluez_output.AA_BB_CC_DD_EE_FF.1`, a wejście `bluez_input.AA:BB:CC:DD:EE:FF`. Poprzedni wybór transportu oczekiwał podkreśleń i dodatkowego sufiksu także dla wejścia. Teraz dopasowuje znormalizowany adres urządzenia. Trzy testy regresji obejmują obie postacie BT i USB: `python3 software/tests/test_bt_pair.py`. Po zmianie sprawdź zarówno domyślne wejście, jak i źródło istniejącego strumienia SvxLink.
