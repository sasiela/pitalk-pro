# Historia zmian PiTalk Pro

Historia opisuje zmiany funkcjonalne i zakres ich sprawdzenia. Szczegóły kodu znajdują się w commitach, a gotowość do odtworzenia urządzenia w [READINESS](docs/project/READINESS.md).

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
