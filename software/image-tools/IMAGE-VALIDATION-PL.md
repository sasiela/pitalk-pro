# PiTalk Pro alpha-1 — weryfikacja obrazu

Data przygotowania: 16 września 2026.

## Sprawdzone

- Obraz dysku 6 GiB, tablica MBR, partycja FAT32 `bootfs` 512 MiB i partycja ext4 `rootfs`.
- Kontrola FAT32 i ext4 zakończona bez błędów.
- Inspekcja obu partycji zamontowanych tylko do odczytu: pliki startowe Raspberry Pi 3, nakładka PiTFT, zgodność PARTUUID z konfiguracją rozruchu i montowania.
- Obecność i uprawnienia programu pierwszego uruchomienia, włączenie jego usługi, składnia głównych programów Python.
- Symulacja pierwszej konfiguracji: ustawienie danych, zapis chronionego profilu Wi-Fi, usunięcie pliku konfiguracyjnego z hasłami oraz brak powtarzania konfiguracji po inicjalizacji.
- Puste konto tożsamości urządzenia (`machine-id`), zablokowane hasła kont przed konfiguracją, brak starych kluczy SSH/HTTPS i profili Wi-Fi.
- Skan plików porównujący zawartość z prywatnymi danymi urządzenia źródłowego. Jedyny wskazany plik był opcjonalnym przykładem dokumentacji cloud-init; został usunięty z obrazu. Raport nie zawiera sekretów.
- Obraz powstał na nowym systemie plików, a nie przez kopiowanie wolnych bloków oryginalnej karty.

## Ograniczenia

Nie zapisano karty microSD i nie uruchomiono fizycznego urządzenia z tego obrazu. Rozruch, powiększanie partycji, pierwsza konfiguracja, kolejność startu usług i działanie sprzętu wymagają testu na zapasowej karcie. Kopię plików pobrano z działającego urządzenia; nie jest to migawka zatrzymanego systemu.

To prywatna wersja testowa, a nie zatwierdzone wydanie do publicznej dystrybucji. Ustawienia działającego urządzenia źródłowego nie zostały zastąpione ustawieniami fabrycznymi obrazu.

## Końcowa kontrola kopii na Macu

- Suma SHA-256 pierwotnego transferu była zgodna z plikiem na Raspberry Pi. Następnie lokalny obraz zaktualizowano o domyślny hostname; aktualna suma znajduje się w `SHA256SUMS`.
- Pełna kontrola gzip: bez błędów.
- Tablica MBR odczytana z lokalnego archiwum: zgodna z planowanym układem partycji.
- Rozmiar skompresowany: 917741140 bajtów (875.2 MiB).
- Rozmiar po rozpakowaniu: 6 442 450 944 bajty (6 GiB).

## Aktualizacja domyślnej nazwy

Ustawiono `hostname` na `pitalk-pro` w `pitalk-setup.json` wewnątrz obrazu i w dołączonym szablonie. Porównanie wszystkich bajtów z poprzednim obrazem potwierdziło zmiany wyłącznie w zawartości tego pliku i jego polu rozmiaru w katalogu FAT32. Partycja root pozostała identyczna. Kontrola FAT32 po aktualizacji nie wykazała błędów. Nazwa zostanie zastosowana przy pierwszym poprawnym skonfigurowaniu nowej instalacji.
