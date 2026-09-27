# Aktualizacje z ekranu PiTALK

W menu głównym wybierz **System Update**. **Check for updates** odczytuje kanał stable w GitHub. **Install update** wymaga osobnego potwierdzenia; Cancel jest domyślne.

Wersja 1 aktualizuje tylko ekran, obsługę enkodera, regulację głośności i menu aktualizacji. Nie aktualizuje panelu WWW, systemu, samego uprzywilejowanego instalatora ani ustawień urządzenia. Panel WWW ma lokalną konfigurację wymagającą wcześniejszego oddzielenia od kodu. To wydanie aplikacji, nie obraz firmware.

Enkoder: A=BCM5/pin29, B=BCM6/pin31, klik=BCM13/pin33, masa=pin39. Na ekranie głównym obrót zmienia głośność co 5%, klik otwiera menu. W menu obrót przewija, klik zatwierdza; BACK pozostaje na przycisku HAT. Użytkownik potwierdził działanie enkodera; kierunek przywrócono do pierwotnego.

## Instalacja aktualizacji

Urządzenie pobiera `software/updates/stable.json` przez HTTPS, następnie manifest i cztery pliki z oznaczonego tagu `pitalk-vX.Y.Z`. Nie wymaga programu Git ani tokenu do publicznego repozytorium. Weryfikuje SHA-256, listę dozwolonych ścieżek i składnię Pythona przed zmianą. Zaufanie opiera się na HTTPS i kontroli repozytorium; nie ma niezależnego podpisu wydania. Nie zmieniaj opublikowanych tagów.

Instalacja wymaga: braku PTT i RX, aktualnego PID w stanie radia, minimum 50 MiB miejsca. Na życzenie właściciela niskie napięcie nie blokuje instalacji. Awaria sieci podczas pobierania nie zmienia działających plików.

Przed podmianą plików powstaje kopia w `/var/lib/pitalk-update/backup` i trwały dziennik `pending.json`. Po restarcie ekranu helper oczekuje na świeży heartbeat po zapisie framebuffer, należący do bieżącego PID; wymagane jest 20 sekund stabilności w czasie do 75 sekund. Przy błędzie przywraca poprzednie pliki. Po przerwaniu instalacji helper przy starcie odtwarza kopię. To kontrola pracy programu, nie fizycznego obrazu LCD ani jakości audio. Zachowywana jest jedna kopia poprzedniej transakcji.

## Pierwsze wdrożenie i wydania

Pierwsze uruchomienie wymaga administratora: instalacja `pitalk-update.py`, jednostki systemd, czterech plików aplikacji i nadanie katalogowi stanu praw 0700. Zainstalowana wersja jest zapisana przez administratora w `/var/lib/pitalk-update/installed.json`. Nie kopiuj całego rootfs ani przykładów konfiguracji nad urządzenie.

Przy kolejnym wydaniu zmień tag w `release.json`, przelicz SHA-256 czterech plików, wykonaj testy, opublikuj commit i nowy tag; dopiero potem wskaż tag w `stable.json`. Po starcie nowej aplikacji operator sprawdza ekran, menu, enkoder i głośność. Dostęp SSH zachowaj jako drogę naprawy.

## Walidacja

`python3 software/tests/test_update.py`: test manifestu, odrzucenia niedozwolonej ścieżki, zapisu atomowego, instalacji i rollbacku na tymczasowych plikach. Nie są to testy odcięcia zasilania na fizycznym urządzeniu. Pierwszy prototyp zgłasza undervoltage; pełnego cyklu instalacji nowego wydania na urządzeniu nie potwierdzono.

### Wdrożenie prototypu — 2026-09-27

Zainstalowano i włączono usługę aktualizatora za zgodą właściciela. Ekran oraz helper aktywne, bez automatycznych restartów; świeży heartbeat po zapisie obrazu. Sprawdzenie GitHub zwróciło `Up to date`, zainstalowana i dostępna wersja `pitalk-v0.1.0`. Urządzenie nadal zgłasza bieżące undervoltage (`0x50005`); pełnej instalacji kolejnego wydania ani fizycznego rollbacku nie testowano.

### Poprawka interfejsu 0.1.2 — 2026-09-27

Wersja `pitalk-v0.1.2` poprawia układ System Update: nagłówek obok ikony powrotu, wspólne zaznaczenie, osobne miejsce na potwierdzenie i maksymalnie trzy linie komunikatu. Wybierz Check for updates, następnie Install update i Install now. Po instalacji sprawdź Current: pitalk-v0.1.2 oraz brak nakładania napisów. Rendery sprawdzono lokalnie; instalacja i wygląd na fizycznym LCD wymagają potwierdzenia właściciela.

### Panel WWW — przygotowany 2026-09-27

System zawiera sekcję System Update: wersje, ręczne sprawdzenie, potwierdzenie instalacji i status odświeżany w tle. API wymaga sesji, operacje POST także CSRF; używa istniejącego ograniczonego helpera. Brak helpera jest widoczny jako niedostępność bez blokowania pozostałego panelu. Sprawdzanie przy starcie urządzenia i monit LCD nie są jeszcze zaimplementowane.

Właściciel potwierdził działanie aktualizacji 0.1.2 z terminala. GitHub + menu urządzenia to uzgodniony kanał aktualizacji. Obecna lista czterech plików nie obejmuje WWW: ta zmiana panelu nie jest jeszcze wdrożona ani oferowana przez stable.json. Rozszerzenie instalatora wymaga osobnej migracji; nie wolno nadpisać prywatnego filtra LAN przykładowym server.py z repozytorium.
