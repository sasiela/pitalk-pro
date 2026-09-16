# PiTalk Pro — instrukcje dla asystenta

## Cel repozytorium

Repozytorium jest wspólnym źródłem projektu dla osób budujących własne urządzenie, nie tylko pakietem przekazania między asystentami. Punktem wejścia dla budujących jest `docs/README.md`. Przy zmianach uzupełniaj instrukcję budowy, testy i `docs/project/READINESS.md`. Nie oznaczaj prototypu lub samej kontroli składni jako potwierdzonej odtwarzalności na nowym urządzeniu.

## Zacznij tutaj

1. Przeczytaj `docs/handoff/START-HERE.md`, `ARCHITECTURE.md`, `OPERATIONS.md` i `KNOWN-ISSUES.md`.
2. Aktualny eksport kodu znajduje się w `software/rootfs/`. Ścieżka poniżej `rootfs/` odpowiada ścieżce na Raspberry Pi. To snapshot, a nie kompletny instalator systemu.
3. `software/manifest.json` opisuje pochodzenie, sumy i oczyszczenie eksportu. Konfiguracje `.example` nie zawierają danych logowania.
4. Jeżeli istnieje ignorowany przez Git `LOCAL-ACCESS.md`, przeczytaj go dla lokalnych ścieżek i dostępu do prototypu. Nie publikuj go.

## Zasady projektu

- Rozmawiaj z właścicielem po polsku, prosto i konkretnie. Interfejs urządzenia i panel WWW pozostają po angielsku. Właściciel oczekuje wykonania pracy, nie tylko instrukcji; nie pytaj ponownie o już udzieloną zgodę.
- Zachowaj istniejące STL, filmy i dokumentację mechaniczną oraz niezapisane zmiany użytkownika.
- Nie zapisuj haseł, kluczy, tokenów, cookies, rzeczywistych profili Wi-Fi, baz kont ani prywatnych backupów w repozytorium. Nie drukuj ich w logach narzędzi. Przykładowe dane muszą pozostać puste lub wyraźnie fikcyjne.
- Samo przekazanie projektu nie oznacza polecenia wdrożenia lub publikacji. Gdy użytkownik zleci zmianę na urządzeniu, sprawdź aktualny stan, wykonaj kopię zmienianych plików, zastosuj wąski zakres zmiany i zweryfikuj wynik.
- Nie kopiuj całego `software/rootfs/` na działające urządzenie. Eksport ma przykładowy filtr LAN w `server.py`; szablony nie mogą nadpisać działającej konfiguracji właściciela.
- Przed restartem sprawdź, czy jest RX lub aktywny PTT. Nie wywołuj rzeczywistego nadawania jako automatycznego testu. Zwolnienie PTT na błędzie/wyjściu jest kluczowym zachowaniem.
- Zachowaj lokalne audio przy zmianach odsłuchu WWW. Odsłuch korzysta z monitora wyjścia, nie przejmuje fizycznej karty.
- Nie utożsamiaj braku połączenia z reflektorem z brakiem Wi-Fi. ONLINE wynika z lokalnego stanu SvxLink; API serwera jest uzupełnieniem.
- UID 1002, GPIO24 jako programowy squelch, GPIO26 jako wejście przycisku i dostęp do sesji audio są zależnościami prototypu. Nie zmieniaj ich bez analizy całego przepływu.
- Testuj adekwatnie: składnia i logika lokalnie, potem konkretna funkcja na urządzeniu, jeśli jest dostęp i zlecenie tego wymaga. Nie uruchamiaj skryptu ekranu na Macu jak zwykłej aplikacji.
- Odróżniaj potwierdzone obserwacje od przypuszczeń. Obraz alpha nie przeszedł fizycznego testu rozruchu. Nie obiecuj działania przez noc ani zgodności z innymi płytkami bez dowodów.
- Nie wykonuj commit/push, zapisu karty ani publicznego wydania w ramach samego zapoznawania się z projektem.

## Źródła prawdy

Nowy odczyt urządzenia > aktualny kod > manifest eksportu i dokumentacja przekazania > wcześniejsze założenia z rozmowy. Gdy kod i opis się różnią, zaznacz różnicę zamiast zgadywać. Aktualizuj dokumentację po kolejnych zmianach.
