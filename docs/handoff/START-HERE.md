# Przekazanie PiTalk Pro do Cursora

Stan przekazania: 16 września 2026. Dokumentacja odtwarza dostępny kontekst prac i została zestawiona z aktualnym kodem pobranym z działającego urządzenia. Nie jest dosłownym archiwum wszystkich rozmów ani zapisem wewnętrznej pamięci asystenta.

Dla osób budujących urządzenie głównym punktem wejścia jest teraz [dokumentacja projektu](../README.md). Ten pakiet zachowuje kontekst techniczny rozwoju.

## Cel i stan

PiTalk Pro to terminal głosowy oparty na Raspberry Pi 3 B z PiTFT, przyciskami i lokalnym PTT. SvxLink łączy go z reflektorem SQLink. Użytkownik steruje terminalem z fizycznego menu lub lokalnego panelu HTTPS. Projekt zawiera również obudowę do druku 3D.

Działają: menu, zarządzanie Wi-Fi/Bluetooth/audio, regulacja głośności, konfiguracja użytkownika, wybór i monitorowanie TG, status odbioru/nadawania, znak nadawcy, wskaźnik audio i panel WWW z odsłuchem. Właściciel wielokrotnie sprawdzał działanie funkcji, ale nie ma kompletnego automatycznego zestawu testów end-to-end.

Ostatnia zmiana działającego prototypu: hostname `pitalk-pro`, utrwalenie go w cloud-init oraz dodanie nowej nazwy do dozwolonych Host panelu. `https://pitalk-pro.local:8443/` odpowiedział HTTP 200 z Maca. Avahi, panel, SvxLink i ekran były aktywne. To obserwacja w chwili sprawdzenia, nie gwarancja bieżącego stanu.

## Co jest w repozytorium

| Ścieżka | Zawartość |
| --- | --- |
| `stl/`, `Video/`, `docs/images/` | Istniejące materiały obudowy i prezentacji; zachowane |
| `software/rootfs/` | Kod aplikacji i usługi pobrane z działającego prototypu |
| `software/examples/` | Szablony konfiguracji sprzętu i SvxLink, bez danych logowania |
| `software/manifest.json` | Lista plików, tryby/uprawnienia źródłowe, sumy i opis anonimizacji |
| `software/image-tools/` | Eksperymentalne narzędzia i dokumentacja obrazu alpha |
| `docs/handoff/` | Architektura, obsługa, historia, ograniczenia i dalsze prace |
| `LOCAL-ACCESS.md` | Lokalne adresy i ścieżki właściciela; ignorowane przez Git |

**Ważne:** eksport nie jest identyczną kopią wdrożenia. W `server.py` prywatny adres i podsieć zastąpiono przykładem `192.168.1.100` / `192.168.1.0/24`. Przy wdrażaniu trzeba świadomie ustawić `local_access()`. Stare aliasy hosta usunięto. Nie zastępuj działającego pliku bez uwzględnienia tej różnicy.

Nie pobrano kont, haseł, tokenu PulseAudio, kluczy SSH/HTTPS, parowań BT, zapisanych Wi-Fi, logów ani prywatnych katalogów. Szablon SvxLink pochodzi z oczyszczonego stagingu obrazu, a nie z aktywnej konfiguracji logowania.

## Kolejność czytania

1. `ARCHITECTURE.md` — przepływ sterowania i audio.
2. `OPERATIONS.md` — pliki stanu, diagnostyka i bezpieczne wdrażanie.
3. `KNOWN-ISSUES.md` — ograniczenia prototypu i obrazu.
4. `HISTORY-AND-UX.md` — decyzje i preferencje właściciela.
5. `IMAGE-AND-BACKUPS.md` — obraz testowy, backupy, filmy.

## Wiadomość startowa do Cursora

> Przeczytaj AGENTS.md i dokumentację docs/handoff. Poznaj aktualny kod software/rootfs oraz manifest eksportu. Odróżnij działający prototyp od obrazu alpha i przykładów konfiguracji. Sprawdź stan repozytorium, podsumuj architekturę i ograniczenia. Nie wdrażaj zmian ani nie publikuj repozytorium, dopóki nie zlecę konkretnej pracy. Rozmawiaj ze mną po polsku; interfejs projektu ma pozostać po angielsku.
