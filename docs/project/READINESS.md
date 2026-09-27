# Kompletność i droga do wydania

Aktualizacja: 16 września 2026. Cel: repozytorium ma wystarczać do zbudowania własnego urządzenia, bez dostępu do prywatnych danych autora.

| Obszar | Stan | Następny konkretny rezultat |
| --- | --- | --- |
| Modele i mechanika | STL, kolejność autora i instrukcja zdjęciowa dostępne | Zdjęcia końcowego zamknięcia i wymiary dystansów |
| Lista części | Referencje dostępne, niektóre identyfikatory niepełne | Numery produktów/USB, zasilanie i komplet audio |
| Schemat | BCM oraz PTT na fizycznych 37/39 opisane i pokazane | Kompletny rysunek montażowy i tor audio |
| Kod | Eksport działającego prototypu i manifest | Konfiguracja niezależna od stałego IP, UID i gpio536 |
| Instalacja od zera | Niekompletna | Powtarzalny instalator z wersją OS i zależności |
| Obraz alpha | Plik lokalny, kontrola struktury i sum wykonana | Rozruch i pełny test na osobnej karcie |
| Pierwsza konfiguracja | Skrypt i symulacja dostępne | Test poprawnych i błędnych danych na sprzęcie |
| Instrukcja użytkownika | Funkcje opisane w dokumentacji rozwoju | Zrzuty i prosta instrukcja każdej funkcji dla nowej osoby |
| Aktualizacja / recovery | Opisane zasady, prywatne backupy istnieją | Sprawdzona procedura aktualizacji i odtworzenia |
| Testy | Statyczne i symulacja; obserwacje prototypu | Wypełniony protokół dla czystej instalacji i drugiego egzemplarza |
| Licencje i materiały źródłowe | Nie ustalono kompletnego zestawu | Decyzja właściciela dla kodu/STL/docs i zachowane informacje o zależnościach |
| Publikowane wydanie | Brak potwierdzonego obrazu wydania | Paczka obrazu + SHA-256 + źródła + instrukcja + raport zgodnych wersji |

## Co znaczy „kompletne”

Nowa osoba potrafi dobrać części, wykonać połączenia, złożyć obudowę, zainstalować system, wprowadzić własne dane, sprawdzić działanie i odtworzyć backup. Każdy potrzebny krok ma opis lub zweryfikowany automat. Wynik został odtworzony na drugim egzemplarzu. Znane ograniczenia są jawne.

## Kolejność uzupełnienia

1. Uzupełnić schemat i konkretne identyfikatory części.
2. Przeprowadzić test alpha na zapasowej karcie i zapisać wyniki.
3. Usunąć zależności od sieci i konta prototypu, przygotować powtarzalną instalację.
4. Poprosić drugą osobę o budowę według dokumentacji i poprawić niejasności.
5. Ustalić licencje, przygotować wersjonowane wydanie i dopiero wtedy udostępnić obraz.

## Zasada utrzymania

Przy zmianie sprzętu aktualizujemy listę części i schemat. Przy zmianie funkcji — instrukcję oraz test. Przy zmianie instalacji — receptę budowy i odtworzenia. Przy wydaniu — raport zgodnej konfiguracji i sumy artefaktów. Prywatne dane użytkowników nie są częścią projektu.

## Aktualizacja — testy audio WWW, 17 września 2026

Dodano test wyjścia oraz miernik mikrofonu. Testy logiki/API i symulacja UI przeszły; na prototypie zweryfikowano procesy USB. Słyszalność, reakcja na mowę i zestaw Bluetooth wymagają potwierdzenia użytkownika. [Zakres i instrukcja](../build/AUDIO-TESTS.md). Obraz alpha-1 bez tej zmiany.

## Aktualizacja — profile, 22 września 2026

Wdrożono wspólne profile reflektorów w menu i WWW, aktywację z przywracaniem konfiguracji oraz wybór domyślnego profilu na rozruch. Import i zapis sprawdzono na prototypie; w końcowej kontroli Fala była już aktywna i połączona. Audio/TG Fali, powrót do SQLink i restart z drugim profilem pozostają do testu. [Instrukcja, wyniki i ograniczenia](../build/PROFILES.md). Obraz alpha-1 bez tej aktualizacji.

## Mechanika — 2026-09-26

Dodano [korpus V39 i front V42 pod EC11](../build/MECHANICAL-EC11.md), w STL i STEP. Potwierdzona przymiarka próbnego górnego odcinka 20 mm; sprawdzona geometria CAD i brak kolizji korpus–front. Do potwierdzenia pozostaje pełny montaż, dobór tylnych śrub, luz enkodera z przewodami oraz jego gałka i obsługa elektryczna/programowa. Poprzedni zestaw V32/V38 zachowano.

## Zestaw do pobrania — 2026-09-27

[Kompletny ZIP STL V39/V42](../../releases/PITalk-Final-STL-V39-V42.zip): 5 modeli, 8 drukowanych części. Sprawdzono zgodność kopii i integralność archiwum. Zakres potwierdzenia montażu pozostaje bez zmian; gałka EC11 nie jest jeszcze gotowa.

## Aktualizator — 2026-09-27

[System Update](../build/UPDATES.md): implementacja i testy lokalne instalacji/rollbacku gotowe. Pełny fizyczny cykl aktualizacji pozostaje do sprawdzenia po rozwiązaniu undervoltage. Nie oznacza gotowego obrazu firmware.

### Wdrożenie prototypu — 2026-09-27

Zainstalowano i włączono usługę aktualizatora za zgodą właściciela. Ekran oraz helper aktywne, bez automatycznych restartów; świeży heartbeat po zapisie obrazu. Sprawdzenie GitHub zwróciło `Up to date`, zainstalowana i dostępna wersja `pitalk-v0.1.0`. Urządzenie nadal zgłasza bieżące undervoltage (`0x50005`); pełnej instalacji kolejnego wydania ani fizycznego rollbacku nie testowano.

### Poprawka interfejsu 0.1.2 — 2026-09-27

Wersja `pitalk-v0.1.2` poprawia układ System Update: nagłówek obok ikony powrotu, wspólne zaznaczenie, osobne miejsce na potwierdzenie i maksymalnie trzy linie komunikatu. Wybierz Check for updates, następnie Install update i Install now. Po instalacji sprawdź Current: pitalk-v0.1.2 oraz brak nakładania napisów. Rendery sprawdzono lokalnie; instalacja i wygląd na fizycznym LCD wymagają potwierdzenia właściciela.

### Panel WWW — przygotowany 2026-09-27

System zawiera sekcję System Update: wersje, ręczne sprawdzenie, potwierdzenie instalacji i status odświeżany w tle. API wymaga sesji, operacje POST także CSRF; używa istniejącego ograniczonego helpera. Brak helpera jest widoczny jako niedostępność bez blokowania pozostałego panelu. Sprawdzanie przy starcie urządzenia i monit LCD nie są jeszcze zaimplementowane.

Właściciel potwierdził działanie aktualizacji 0.1.2 z terminala. GitHub + menu urządzenia to uzgodniony kanał aktualizacji. Obecna lista czterech plików nie obejmuje WWW: ta zmiana panelu nie jest jeszcze wdrożona ani oferowana przez stable.json. Rozszerzenie instalatora wymaga osobnej migracji; nie wolno nadpisać prywatnego filtra LAN przykładowym server.py z repozytorium.

### Rozszerzony instalator i wydanie 0.1.3

Jednorazowa migracja prototypu 2026-09-27 zachowała filtr LAN w `/etc/sqlink-web/access.json` i rozszerzyła helper o siedem plików WWW (łącznie 11 plików wydania). Usługa działa; kopia poprzedniego helpera i unitu jest w `/var/backups/pitalk-web-bootstrap-20260927-194540`. Aplikacja pozostała 0.1.2 do instalacji z menu.

0.1.3 dostarcza panel WWW z aktualizacjami. Instalacja restartuje ekran i WWW (sesja przeglądarki oraz odsłuch zostaną przerwane); kontroluje heartbeat ekranu, aktywność WWW i odpowiedź HTTPS przez 20 sekund. W razie błędu przywraca wszystkie pliki transakcji. Stare wydania czteroplikowe pozostają obsługiwane. Stary helper nie zainstaluje wydania 11-plikowego: wymaga najpierw migracji administracyjnej.

Na nowym urządzeniu utwórz `/etc/sqlink-web/access.json` zgodnie z `software/examples/sqlink-web-access.json.example`, ustawiając rzeczywistą podsieć i dozwolone nazwy. Brak konfiguracji blokuje dostęp, nie otwiera panelu. Plik jest poza wydaniem i nie jest nadpisywany przez update. Fizyczny test instalacji 0.1.3 oczekuje na operatora. Automatyczny monit po starcie nadal nie jest częścią tej wersji.

### System Info — 0.1.4

Dodano zakładkę WWW System Info: wersja zainstalowana i ostatnio sprawdzona, model, hostname, OS, kernel, architektura, uptime, temperatura CPU oraz bieżące i historyczne flagi napięcia/throttlingu. Dane są migawką odświeżaną przy otwarciu lub przyciskiem Refresh. Brak źródła oznacza Unavailable. API wymaga logowania. Testy obejmują 0x0, 0x50000, 0x50005 i niedostępne czujniki; wygląd i odczyty na fizycznym urządzeniu wymagają potwierdzenia po instalacji. Wydanie korzysta z rozszerzonego aktualizatora WWW.

### System Info na PiTFT — 0.1.5

Menu urządzenia ma trzy strony: Software, Hardware, Power status. UP/DOWN lub obrót enkodera zmienia stronę, ENTER odświeża, BACK wraca do menu. Odczyty odbywają się w tle, także co 10 sekund podczas otwartego okna. Niedostępne wartości oznaczono Unavailable. Sprawdzono rendery 240×320 i składnię; fizyczny wygląd pozostaje do potwierdzenia po instalacji. Nie wymaga kolejnej migracji helpera.
