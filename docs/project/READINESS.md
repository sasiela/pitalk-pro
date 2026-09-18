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
