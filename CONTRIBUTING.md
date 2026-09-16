# Rozwijanie i uzupełnianie PiTalk Pro

Celem zmian jest umożliwienie innym zbudowania i utrzymania własnego urządzenia. Zacznij od [dokumentacji](docs/README.md) i [statusu kompletności](docs/project/READINESS.md).

## Co dołączać do zmiany

- Opis konkretnego problemu i działania po zmianie.
- Kod, dokumentację lub model, którego zmiana dotyczy.
- Sposób sprawdzenia i ograniczenia testu. Test na prototypie nie oznacza testu czystej instalacji.
- Przy sprzęcie: dokładny model, wersję STL, pomiary i podpisane zdjęcia.
- Przy zależnościach: wersję, pochodzenie i istniejące informacje licencyjne.

Nie oznaczaj propozycji jako działającej funkcji. Zachowuj wersje STL i opisuj zgodność części. Nie zastępuj istniejących materiałów użytkownika bez sprawdzenia ich zmian.

## Zgłaszanie błędu

Podaj wersję kodu/obrazu, model Pi, ekran, audio, OS, objaw, kroki odtworzenia i oczekiwany wynik. Dla OFFLINE rozróżnij sieć lokalną od reflektora. Dołącz krótki oczyszczony log; usuń hasła, tokeny, adresy i identyfikatory, których nie chcesz upubliczniać.

## Dokumentacja i prywatność

Wiedza wspólna trafia do `docs/`, kod do `software/`, geometria do `stl/`. Historia techniczna pozostaje w `docs/handoff/`, ale instrukcja budowy nie może zależeć od lokalnych ścieżek autora. `LOCAL-ACCESS.md` i prywatne backupy pozostają poza Git. Zdjęcia przed publikacją wymagają sprawdzenia zawartości i metadanych; obecność pliku w katalogu roboczym nie oznacza, że został przejrzany do wydania.

Teksty interfejsu pozostają po angielsku. Instrukcje dla użytkowników powinny mieć prosty język i czytelne oznaczenie testów. Dokumentacja techniczna może być rozwijana równolegle po polsku i angielsku; tłumaczenia muszą odzwierciedlać tę samą wersję.

Licencje całego zestawu nie zostały jeszcze ustalone. Zachowuj istniejące nagłówki i pochodzenie plików; nie dodawaj w imieniu autorów niewybranej licencji.
