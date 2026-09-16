# Instalacja i pierwsze uruchomienie

## Wybierz właściwą ścieżkę

| Ścieżka | Stan |
| --- | --- |
| Gotowy obraz dla nowej karty | Plik alpha istnieje lokalnie u autora; kontrole pliku przeszły, test rozruchu nie został wykonany. Brak publicznego pliku wydania. |
| Instalacja od czystego systemu | Eksport kodu i przykłady są dostępne. Nie ma kompletnego, przetestowanego instalatora ani przypiętej listy pakietów. |
| Zmiana istniejącego PiTalk Pro | Dla rozwijających prototyp: wąskie wdrożenie wybranych plików po odczytaniu bieżącej konfiguracji. |

**Pobranie repozytorium nie daje jeszcze gotowego do wgrania firmware.** Katalog `software/rootfs/` nie jest pełnym systemem i nie powinien być kopiowany zbiorczo na Raspberry Pi.

## Pierwsza konfiguracja obrazu alpha

Jeżeli otrzymałeś obraz od autora do testów, użyj [instrukcji alpha](../../software/image-tools/IMAGE-INSTALL-PL.md) oraz odpowiadającego mu pliku SHA256SUMS. Opublikowane wydanie powinno w przyszłości zawierać obraz, jego sumę, numer wersji i wyniki testów razem. Nie używaj obrazu skonfigurowanego wcześniej przez inną osobę jej hasłami.

Skrót procesu:

1. Zapisz obraz na osobnej karcie minimum 8 GB w Raspberry Pi Imager, używając własnego obrazu. W tej wersji pomiń personalizację Imagera.
2. Otwórz `pitalk-setup.json` na bootfs i ustaw własne `system_password` zgodnie z instrukcją. Zachowaj poprawny JSON.
3. Hostname domyślnie `pitalk-pro`. Przy kilku urządzeniach w jednej sieci nadaj każdemu inną nazwę.
4. Wpisz Wi-Fi lub użyj LAN. Opcjonalnie wpisz własne dane reflektora; konto reflektora trzeba posiadać niezależnie od tego projektu.
5. Po starcie sprawdź wynik konfiguracji i dostęp do `https://pitalk-pro.local:8443`. Gdy mDNS nie działa, użyj IP z routera/menu.
6. Zaloguj się jako `sqlink` własnym hasłem systemowym. W razie potrzeby skonfiguruj User, Audio i Wi-Fi na urządzeniu lub w panelu.
7. Wypełnij [protokół testu](../testing/ACCEPTANCE.md), w tym ponowny rozruch.

Hasło systemowe do panelu/SSH oraz hasło reflektora to różne dane. Obraz nie tworzy konta na serwerze SQLink. Funkcja zmiany hosta reflektora nie oznacza jeszcze pełnej niezależności od SQLink: adresy API nazw TG i statusu również wymagają przeglądu przy użyciu własnego serwera.

## Czego brakuje do instalacji od czystego OS

Potrzebny jest sprawdzony proces obejmujący:

- wersję bazowego OS i pakietów;
- konto aplikacji, grupy i sesję audio; obecnie część ścieżek zakłada UID 1002;
- PiTFT/framebuffer, uprawnienia GPIO i mapowanie programowego squelcha;
- PipeWire/WirePlumber/BlueZ oraz poprawne wejście i wyjście audio;
- SvxLink, konfigurację logik i handler zdarzeń;
- helpery, sockety i zależności systemd;
- PAM, własny certyfikat HTTPS i filtr lokalnego dostępu dopasowany do sieci;
- generowanie własnej tożsamości urządzenia i sposób aktualizacji/wycofania zmian.

Źródłem szczegółów są [architektura](../handoff/ARCHITECTURE.md), [obsługa](../handoff/OPERATIONS.md) i pliki kodu. Lista powyżej jest zakresem brakującego instalatora, nie sekwencją poleceń do wykonania.

## Gdy pojawi się problem

Nie zaczynaj od ponownego wgrywania systemu. Rozdziel diagnostykę: zasilanie/rozruch, ekran, sieć lokalna, usługi, logowanie do reflektora, wejście/wyjście audio. OFFLINE przy działającym panelu może oznaczać problem połączenia SvxLink, a nie brak Wi-Fi. Opisz objaw i etap testu zgodnie z [CONTRIBUTING.md](../../CONTRIBUTING.md).
