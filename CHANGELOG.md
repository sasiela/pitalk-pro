# Historia zmian PiTalk Pro

Historia opisuje zmiany funkcjonalne i zakres ich sprawdzenia. Szczegóły kodu znajdują się w commitach, a gotowość do odtworzenia urządzenia w [READINESS](docs/project/READINESS.md).

## 2026-09-27 — System Info na urządzeniu 0.1.5

- Trzy strony informacji w menu PiTFT: wersja i system, sprzęt i temperatura, bieżące oraz historyczne błędy zasilania.
- Odczyty w tle, przełączanie enkoderem i odświeżanie kliknięciem. Sprawdzono podglądy wszystkich stron.

## 2026-09-27 — System Info 0.1.4

- Nowa zakładka WWW z informacjami o urządzeniu, wersji aplikacji, systemie i temperaturze.
- Bieżące błędy zasilania oddzielono od flag historycznych; brak danych nie oznacza poprawnego zasilania.
- Sprawdzono składnię JS/Python, 11 testów API i 7 testów aktualizatora. Fizyczny test panelu po aktualizacji pozostaje do potwierdzenia.

## 2026-09-27 — Wydanie 0.1.3 i migracja WWW

- Rozszerzono aktualizator prototypu o WWW, zachowując prywatną konfigurację LAN poza plikami aplikacji.
- Wydanie 0.1.3 zawiera panel System Update. Kontrola działania obejmuje ekran i odpowiedź HTTPS; rollback obejmuje cały zestaw.
- Aktualizacja restartuje również WWW i wymaga ponownego zalogowania. Test fizycznej instalacji 0.1.3 pozostaje do potwierdzenia.

## 2026-09-27 — Panel WWW: obsługa aktualizacji (przygotowana)

- Dodano System Update z wersjami, sprawdzaniem, potwierdzeniem instalacji i odświeżaniem statusu.
- Nowe API korzysta z sesji, CSRF i ograniczonego helpera urządzenia. Wdrożenie WWW wymaga rozszerzenia obecnego aktualizatora; kanał stable pozostaje 0.1.2.

## 2026-09-27 — System Update 0.1.2

- Dopasowano nagłówek, separatory i zaznaczenie do pozostałych menu. Usunięto dodatkową etykietę wersji testowej; wersja instalacji pozostaje w Current.
- Potwierdzenie instalacji i komunikaty mają oddzielne obszary. Długie teksty są ograniczane według szerokości w pikselach.
- Sprawdzono rendery 240×320 okna głównego, potwierdzenia i długiego błędu; fizyczny test instalacji przez menu pozostaje do wykonania.

## 2026-09-27 — Wydanie testowe 0.1.1

- Dodano widoczny napis `Update UI v0.1.1` w menu aktualizacji, aby potwierdzić załadowanie nowego kodu po instalacji z urządzenia.
- Pozostałe trzy pliki aplikacji bez zmian. Wydanie przeznaczone do pierwszego fizycznego testu aktualizatora; wynik testu nie jest jeszcze potwierdzony.

## 2026-09-27 — Aktualizacje bez blokady napięcia

- Na wyraźne życzenie właściciela usunięto sprawdzanie undervoltage z blokady instalacji. Zachowano kontrolę RX/PTT, wolnego miejsca, kopię i rollback. Zaktualizowano usługę na terminalu.

## 2026-09-27 — Enkoder i aktualizator aplikacji 0.1.0

- Zapisano działającą obsługę EC11 i głośności z terminala.
- Dodano System Update: oznaczone wersje GitHub, kontrola sum, kopia i automatyczne wycofanie.
- Wersja 1 obejmuje cztery pliki ekranu/enkodera; blokuje instalację podczas RX/PTT i przy niskim napięciu.
- Testy transakcji i wycofania na plikach tymczasowych; fizyczny cykl aktualizacji wymaga jeszcze potwierdzenia. [Instrukcja](docs/build/UPDATES.md).

## 2026-09-27 — Kompletny zestaw STL V39/V42

- Dodano katalog i ZIP: korpus V39, front V42, nakładka V11 (druk 4 szt.), podstawa anteny i antena 70 mm. Nazwy plików po angielsku.
- Sprawdzono zgodność kopii z plikami źródłowymi i integralność ZIP. Gałka enkodera pozostaje do zaprojektowania.

## 2026-09-26 — Korpus V39 i front V42 pod EC11

- Dodano STL i edytowalne STEP; zachowano wcześniejsze części.
- Wydłużono górę o 8 mm pod jeden EC11 i antenę, zamknięto slot microSD i ujednolicono zewnętrzne ścianki.
- Dodano tylne otwory Ø3.4 z gniazdami Ø6.4 / 2.2; wyśrodkowano 40 otworów dna względem śrub.
- Front V42 ma dwa rzędy po trzy otwory nad ekranem.
- Sprawdzono CAD i import STEP; autor potwierdził przymiarkę próbnego górnego odcinka. Pełny montaż i integracja enkodera pozostają do sprawdzenia. [Szczegóły](docs/build/MECHANICAL-EC11.md).

## 2026-09-22 — Czytelniejszy nagłówek profilu

- Po ocenie układu stopki przeniesiono profil pod znak wywoławczy, ponad górną linię.
- Nazwa jest wyśrodkowana, ma większą czcionkę i korzysta z szerokości nagłówka; długie nazwy zachowują wielokropek.
- Stopka zawiera ponownie ikonę menu i zegar. Sprawdzono podgląd krótkiej i długiej nazwy; wdrożono po kopii skryptu.

## 2026-09-22 — Nazwa profilu obok zegara

- Przeniesiono aktywny profil z górnej części ekranu na dół, między ikonę menu a godzinę.
- Dostępna szerokość uwzględnia zegar; długie nazwy kończą się wielokropkiem.
- Sprawdzono renderowanie krótkiej i długiej nazwy. Przed wdrożeniem zapisano kopię skryptu; restart obejmuje tylko ekran.

## 2026-09-22 — Profile reflektorów

### Funkcje

- Wspólne profile połączenia w menu PiTFT i panelu WWW: dodawanie, edycja, aktywacja, profil domyślny na rozruch oraz usuwanie.
- Import istniejącego konta do SQLink i utworzenie osobnego profilu Fala dla `fala.zasieg.pl`, bez kopiowania hasła SQLink.
- Zapis ustawień oddzielony od aktywacji; każdy profil przechowuje własny serwer, port, konto i TG.
- Blokada przełączenia podczas PTT/RX, ochrona przed równoległą edycją oraz przywracanie konfiguracji przy nieudanej aktywacji.
- Nazwa aktywnego profilu na ekranie głównym i w panelu; dane stacji SQLink nie są pobierane dla profilu bez wybranego katalogu SQLink.

### Sprawdzenie i ograniczenia

- 12 testów backendu, 3 testy menu/API oraz 5 testów ochrony HTTP zakończonych powodzeniem. Symulacja WWW obejmuje formularze, pomijanie pustego hasła i układ mobilny.
- Na prototypie sprawdzono import, zapis/usunięcie profilu testowego, odrzucenie niepełnej konfiguracji i renderowanie menu. Końcowy odczyt potwierdził aktywne połączenie Fali.
- Przed wdrożeniem wykonano prywatny backup aplikacji i konfiguracji na urządzeniu i Macu; sumy kopii były zgodne. Backup nie jest częścią repozytorium.
- Audio/TG Fali, powrót do SQLink i rozruch z innym profilem wymagają dalszych testów. Obraz alpha-1 nie został przebudowany.

[Instrukcja i odtwarzanie](docs/build/PROFILES.md) · [Sumy plików aktualizacji](software/profiles-release.json)

## Wcześniejsze prace

Przekazanie projektu, testy audio i poprawka dopasowania mikrofonu Bluetooth są opisane w [dokumentacji rozwoju](docs/handoff/START-HERE.md), [testach audio](docs/build/AUDIO-TESTS.md) i dotychczasowej historii Git. Nie przypisujemy im nowych numerów wydania firmware.
