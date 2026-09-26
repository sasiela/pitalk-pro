# Zbuduj własny PiTalk Pro

Najnowsza mechanika: [korpus V39 i front V42 pod EC11 — pliki, wymiary i zakres testów](MECHANICAL-EC11.md). Pełny montaż tej wersji wymaga jeszcze sprawdzenia.

Przewodnik dla sprzętu zgodnego z prototypem: Raspberry Pi 3 Model B i PiTFT 2.2 cala. To ścieżka rozwojowa; pełna budowa według tej instrukcji przez drugą osobę nie została jeszcze potwierdzona.

| Etap | Materiały | Wynik, który powinieneś uzyskać |
| --- | --- | --- |
| 1. Sprawdź kompletność | [Status projektu](../project/READINESS.md) | Wiesz, które kroki są potwierdzone, a które wymagają pracy |
| 2. Dobierz części | [Lista sprzętu](HARDWARE.md), [BOM CSV](parts.csv) | Zgodne części i sprawdzone wymiary przed drukiem |
| 3. Wydrukuj i dopasuj | [Instrukcja montażu ze zdjęciami](ASSEMBLY.md), [STL](../../stl/) | Swobodny ruch przycisków i poprawne mocowanie elektroniki |
| 4. Zweryfikuj połączenia | [GPIO i audio](HARDWARE.md#połączenia) | Sprawdzony przycisk, zasilanie i tor audio; brak nieopisanych połączeń |
| 5. Przygotuj system | [Instalacja](SOFTWARE.md) | Własny system i konto, bez danych autora |
| 6. Skonfiguruj terminal | [Pierwsze uruchomienie](SOFTWARE.md#pierwsza-konfiguracja-obrazu-alpha) | Wi-Fi/LAN, panel, własne dane reflektora i wybrany tor audio |
| 7. Sprawdź urządzenie | [Protokół testu](../testing/ACCEPTANCE.md) | Zapisany wynik testów, także po restarcie |
| 8. Zachowaj działającą wersję | [Backupy](../handoff/IMAGE-AND-BACKUPS.md) | Prywatna kopia własnego systemu i opis wersji |

## Zanim rozpoczniesz

Nie zakładaj zgodności innych Raspberry Pi, wyświetlaczy lub podobnie nazwanych kart USB. Zapisz użyte modele i wersję plików STL. Projekt ma programowy PTT do SvxLink; ozdobna antena nie jest anteną nadajnika RF. Rozmowy o zewnętrznym radiotelefonie lub EchoLink nie oznaczają, że taki interfejs jest tu gotowy.

Jeżeli dany krok nie ma pełnej instrukcji, zgłoś brak i dołącz opis rozwiązania po jego sprawdzeniu. Nie przedstawiaj nieprzetestowanej sekwencji poleceń jako sprawdzonej instrukcji budowy.
