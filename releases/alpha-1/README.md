# PiTalk Pro alpha-1 — obraz SD

W lokalnym folderze projektu znajduje się `PiTalk-Pro-alpha-1.img.gz`, z domyślną nazwą `pitalk-pro`. Jest to oczyszczony obraz testowy przygotowany 16 września 2026, nie prywatny backup aktywnych ustawień urządzenia.

W Raspberry Pi Imager wybierz **Use Custom / Użyj własnego obrazu** i wskaż plik `.img.gz`; nie trzeba go rozpakowywać. Użyj osobnej karty minimum 8 GB. Zapis usunie jej zawartość. W tej wersji pomiń personalizację Imagera, a po zapisie uzupełnij `pitalk-setup.json` na partycji bootfs zgodnie z [instrukcją](Instrukcja-PL.md).

Obraz przeszedł kontrolę struktury i integralności, ale **nie wykonano fizycznego testu rozruchu**. [Raport testu](Raport-testu.md). Suma kopii w tym katalogu została sprawdzona względem `SHA256SUMS`.

Duży plik obrazu jest wykluczony przez `.gitignore`: znajduje się lokalnie w projekcie, lecz nie zostanie dodany przez zwykłe `git add`. Nie został wysłany na GitHub ani opublikowany jako wydanie. Dokumentacja i suma kontrolna mogą być wersjonowane; do publikacji obrazu należy osobno przygotować artefakt wydania.
