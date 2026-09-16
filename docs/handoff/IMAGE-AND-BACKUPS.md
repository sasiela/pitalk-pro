# Obraz, backupy i nagrania

## Obraz testowy

Przygotowano `PiTalk-Pro-alpha-1.img.gz`, około 878 MiB po kompresji, 6 GiB po rozpakowaniu, MBR, FAT32 bootfs 512 MiB i ext4 rootfs. Do późniejszego testu potrzebna jest osobna karta minimum 8 GB. Nie zapisano karty ani nie sprawdzono fizycznego rozruchu.

W Raspberry Pi Imager: Use Custom, wskazanie `.img.gz`, pominięcie personalizacji Imagera w tej wersji. Po zapisie konfiguracja przez `pitalk-setup.json` na partycji bootfs widocznej w macOS. Domyślny hostname został zmieniony na `pitalk-pro` w lokalnym obrazie. Hasło systemowe wymagane, dane Wi-Fi i reflektora opcjonalne. Login nowej instalacji to `sqlink`; nie ma wspólnego fabrycznego hasła.

Pierwszy start generuje tożsamość/klucze/certyfikat, ustawia konto, sieć i konfigurację reflektora, próbuje rozszerzyć rootfs i usuwa wejściowy plik konfiguracji. Wynik zapisuje do `PITALK-STATUS.txt`. Gdy danych reflektora nie podano, radio ma pozostać niepołączone do uzupełnienia User. Dokładny opis: `software/image-tools/IMAGE-INSTALL-PL.md`.

Kontrole: skan danych prywatnych, kontrole FAT/ext4, inspekcja read-only plików boot i PARTUUID, składnia, symulacja provisioning, pełny gzip i SHA-256 na Macu. Przy zmianie hostname porównano cały rozpakowany obraz; zmieniono tylko JSON na FAT i jego rozmiar w katalogu. Rootfs pozostał identyczny. `software/image-tools/SHA256SUMS` dotyczy końcowej kopii lokalnej, a nie wcześniejszej kopii na Pi.

## Narzędzia budowy

`software/image-tools/` to dokumentacja i eksperymentalne składniki procesu, **nie samodzielny instalator ani gotowy pipeline do uruchomienia w dowolnym katalogu**. Budowa pierwotnie korzystała z `/var/tmp/pitalk-image-alpha/{root,boot,payload}` na Pi, oczyszczonego stagingu i raportu audytu. Pliki `sanitize.py` oraz `build-image.sh` zakładają przygotowane środowisko Linux i uprawnienia root. Identyfikatory właściciela w sanitizerze zastąpiono placeholderami; przed ponownym użyciem trzeba je dopasować i przeprowadzić nowy audyt. Narzędzie audytu porównujące prawdziwe hasła pozostało poza tym pakietem.

Nie dołączono wielogigabajtowego obrazu do Git. Jest w lokalnych artefaktach wskazanych w ignorowanym `LOCAL-ACCESS.md`. Nie uruchamiaj buildera na urządzeniu blokowym oryginalnej karty. Budowa tworzy zwykły plik i używa loop-device tylko dla niego.

## Backup a obraz dystrybucyjny

Istnieją prywatne backupy systemu z 14 i 15 września. Są starsze od finalnej funkcji WWW/odsłuchu i zawierają prywatną konfigurację. Nie publikować ani nie używać bez oczyszczenia jako obrazu dla innych użytkowników. Ich ścieżki znajdują się w `LOCAL-ACCESS.md`.

Obraz alpha powstał z nowszej kopii plików na świeżym systemie plików. Nie przenosił wolnych bloków starej karty. Jest bazą testu dystrybucyjnego, nie zamiennikiem prywatnego backupu ustawień właściciela.

## Filmy

Istnieją osobne prezentacje: panel WWW, rozszerzony panel z odsłuchem, krótki film ekranu fizycznego oraz pełny przegląd ekranu (~6:42, 67 kroków). Pliki mają polskie napisy i syntetycznego lektora. Materiały w `Video/` zachowano. Dodatkowe lokalizacje są w `LOCAL-ACCESS.md`; nie kopiowano automatycznie wszystkich dużych plików do repozytorium.

## Kopia w folderze projektu

Aktualny lokalny obraz z hostname `pitalk-pro` skopiowano również do `releases/alpha-1/PiTalk-Pro-alpha-1.img.gz`. Obok znajdują się suma SHA-256, szablon konfiguracji, instrukcja i raport. Plik obrazu jest ignorowany przez Git i nie został opublikowany.
