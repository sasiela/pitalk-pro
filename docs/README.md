# PiTalk Pro — dokumentacja projektu

Celem repozytorium jest umożliwienie innej osobie zbudowania, skonfigurowania i rozwijania własnego PiTalk Pro. Wspólnie przechowujemy obudowę, kod, konfiguracje przykładowe, instrukcje i wyniki testów. Wiedza potrzebna do budowy nie powinna wymagać dostępu do prywatnej rozmowy ani komputera autora.

**Stan: działający prototyp i dokumentowana wersja rozwojowa.** Instrukcja odtworzenia na czystej karcie nie została jeszcze potwierdzona. Nie ma opublikowanego, przetestowanego wydania obrazu ani kompletnego instalatora. Braki są widoczne w [statusie odtwarzalności](project/READINESS.md).

## Chcę zbudować urządzenie

1. [Przewodnik budowy](build/README.md) — kolejność prac i punkty kontrolne.
2. [Sprzęt i połączenia](build/HARDWARE.md) — części, GPIO i brakujące dane.
3. [Montaż krok po kroku ze zdjęciami](build/ASSEMBLY.md) oraz [pliki STL](../stl/).
4. [Instalacja i pierwsza konfiguracja](build/SOFTWARE.md) — dostępne ścieżki i ich ograniczenia.
5. [Test własnego egzemplarza](testing/ACCEPTANCE.md) — co sprawdzić przed uznaniem budowy za zakończoną.

## Chcę używać lub rozwijać projekt

- [Architektura](handoff/ARCHITECTURE.md) i [obsługa/diagnostyka](handoff/OPERATIONS.md).
- [Znane problemy](handoff/KNOWN-ISSUES.md) oraz [historia decyzji interfejsu](handoff/HISTORY-AND-UX.md).
- [Kod](../software/README.md), [zasady współpracy](../CONTRIBUTING.md), [instrukcje dla asystentów](../AGENTS.md).
- [Obraz i backupy](handoff/IMAGE-AND-BACKUPS.md), [status przygotowania wydania](project/READINESS.md).

Materiały w `docs/handoff/` zachowują kontekst rozwoju. Niniejszy katalog jest punktem wejścia dla wszystkich budujących, niezależnie od używanego edytora lub asystenta.

## Profile połączenia

[Konfiguracja i obsługa profili SQLink / Fala](build/PROFILES.md) — wspólne dla ekranu i panelu WWW.
