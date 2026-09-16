# PiTalk Pro — obraz testowy alpha-1

Obraz zawiera aktualny system PiTalk Pro: ekran PiTFT, menu urządzenia, PTT, obsługę Wi-Fi i Bluetooth, SvxLink oraz panel WWW z odsłuchem audio.

## Zakres testu

Przygotowano plik obrazu. Nie zapisano żadnej karty i nie wykonano fizycznego testu uruchomienia. Wersja jest przeznaczona do prywatnych testów, jeszcze nie do publicznej dystrybucji.

Sprzęt odniesienia: Raspberry Pi 3 Model B Rev 1.2, wyświetlacz PiTFT 2,2 cala 240×320 z nakładką `pitft22`, przyciski GPIO17/22/23/27, PTT GPIO26 i karta dźwiękowa USB. Inne modele Raspberry Pi i ekrany nie są potwierdzone.

## Wgranie na zapasową kartę

1. Przygotuj osobną kartę microSD minimum 8 GB. Zapis obrazu usunie jej dotychczasową zawartość.
2. W Raspberry Pi Imager wybierz **Use Custom / Użyj własnego obrazu** i plik `PiTalk-Pro-alpha-1.img.gz`. Nie trzeba go rozpakowywać.
3. Wybierz kartę. W tej wersji **pomiń personalizację systemu w Imagerze**; używamy własnego pliku konfiguracji.
4. Po zapisie i weryfikacji ponownie włóż kartę do Maca. Otwórz widoczną partycję `bootfs`.
5. Edytuj `pitalk-setup.json` jako zwykły tekst, zachowując poprawną składnię JSON. Ustaw własne `system_password` — 12–128 znaków, bez dwukropka. Nie ma wspólnego fabrycznego hasła.
6. Jeśli używasz Wi-Fi, uzupełnij `wifi_ssid`, `wifi_password` i kod kraju `wifi_country`. Przy pierwszym teście można użyć Ethernetu i pozostawić pola sieci puste. Ta wersja obsługuje w pliku konfiguracji sieci WPA Personal.
7. Dane reflektora są opcjonalne. Podaj własne `callsign` i `reflector_password` albo zostaw oba puste i skonfiguruj je później w **Menu → User**. Hasło reflektora i hasło systemowe to dwie różne rzeczy.
8. Bezpiecznie wysuń kartę i uruchom Raspberry Pi. Pierwsza konfiguracja może potrwać kilka minut.

## Pierwsze uruchomienie

System generuje nowe klucze SSH i własny certyfikat HTTPS, ustawia hasło konta `sqlink`, konfiguruje sieć i podejmuje próbę powiększenia partycji root na całą kartę. Domyślna nazwa w pliku konfiguracji to `pitalk-pro`. Panel będzie dostępny pod `https://pitalk-pro.local:8443`, jeśli sieć obsługuje nazwy mDNS `.local`. Możesz zmienić nazwę; puste pole `hostname` tworzy unikalną nazwę `pitalk-xxxxxx`.

Po poprawnej konfiguracji plik `pitalk-setup.json` jest nadpisywany i usuwany. Wynik znajduje się w `PITALK-STATUS.txt` na partycji bootfs. Jeżeli konfiguracja się nie uda, popraw JSON i uruchom urządzenie ponownie.

Panel: `https://ADRES-IP:8443` albo `https://NAZWA.local:8443`.

Login WWW i SSH: **sqlink**. Hasło: własne `system_password`. Polecenia administracyjne `sudo` wymagają tego hasła; logowanie SSH bezpośrednio jako root jest wyłączone.

Adres IP sprawdzisz w **Menu → WiFi** albo w routerze. Certyfikat jest lokalny i samopodpisany, więc przeglądarka pokaże ostrzeżenie — przed zaakceptowaniem sprawdź adres urządzenia.

Jeśli nie wpisano danych reflektora, radio pozostaje niepołączone. Wprowadź własne konto w **Menu → User → Save & reconnect**.

## Kontrola obrazu

- Sprawdź sumę pliku poleceniem `shasum -a 256 -c SHA256SUMS` w katalogu obrazu.
- Raporty dołączone do obrazu opisują kontrolę partycji, systemów plików i skan danych właściciela.
- Obraz zbudowano na nowym systemie plików z oczyszczonych plików; nie jest to surowa kopia karty zawierająca jej stare wolne bloki.
- Nie przeniesiono oryginalnych haseł, profili Wi-Fi, parowań Bluetooth, kluczy SSH/HTTPS, prywatnych katalogów, logów ani tymczasowego dostępu sudo.

## Co sprawdzić na karcie

Rozruch, pierwszy start, Wi-Fi/Ethernet, własne logowanie, ekran i wszystkie przyciski, PTT, karta USB, zestaw Bluetooth, zmiana TG, panel WWW i odsłuch. Rozszerzenie partycji oraz kolejność startu usług także wymagają potwierdzenia na fizycznym sprzęcie.

Przed publicznym wydaniem pozostają testy na czystych kartach i przygotowanie kompletnego pakietu źródeł, licencji oraz informacji o zależnościach. Obsługa opcji personalizacji bezpośrednio w Imagerze może zostać dodana w następnej wersji.
