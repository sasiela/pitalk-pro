# Profile reflektorów — SQLink, Fala i własne serwery

PiTalk Pro przechowuje do 12 profili zgodnych ze SvxReflector. W danej chwili działa jedno połączenie. Każdy profil ma własne: nazwę, host, port, login/znak, hasło, domyślną TG, monitorowane TG oraz czas powrotu do monitorowania. Wi-Fi, Bluetooth i poziomy audio są wspólne.

## Obsługa

- Ekran: **Main Menu → User** otwiera **Profiles**. UP/DOWN wybiera profil, ENTER otwiera jego działania, BACK wraca. **Add profile** tworzy nowy profil.
- Panel: **User → Profiles** (`/#user`). Dostępne są **Add profile, Edit, Activate, Set default, Delete**.
- **Save profile** zapisuje ustawienia bez rozłączania. Zmiany aktywnego profilu wymagają **Activate / Apply & activate**. Domyślny profil podczas kolejnego rozruchu używa swoich zapisanych ustawień.
- **Activate** wymaga hosta, portu, loginu i hasła, blokuje przełączenie podczas PTT/RX, zmienia konfigurację i restartuje SvxLink. Czeka do około 20 sekund na potwierdzenie uwierzytelnienia po restarcie. Przy niepowodzeniu odtwarza poprzednią konfigurację i uruchamia ją ponownie.
- **Set default** nie przełącza aktualnego połączenia. Wskazuje profil stosowany przed uruchomieniem SvxLink przy następnym starcie urządzenia. Nie restartuje urządzenia. Weryfikacja połączenia i powrót do poprzedniego profilu dotyczy aktywacji z menu/API; usługa rozruchowa tylko przygotowuje konfigurację i nie sprawdza dostępności serwera.
- Nie można usunąć aktywnego ani domyślnego profilu. Najpierw wybierz inny. Usunięcie ma chroniony backup na urządzeniu.
- Puste pole hasła podczas edycji zachowuje istniejące hasło. Formularze nie odczytują go z urządzenia. Aby użyć innych danych, wpisz nowe hasło.

## Pierwsze uruchomienie i Fala

Migracja importuje aktualną konfigurację do profilu **SQLink**, ustawia go jako aktywny/domyślny i nie zmienia działającego połączenia. Profil **Fala** powstaje z hostem `fala.zasieg.pl`, pustym portem, loginem i hasłem. Nie kopiuje danych konta SQLink. Uzupełnij właściwy port i konto po przygotowaniu własnego serwera; dopiero wtedy można go aktywować.

**Station directory** określa źródło nazw TG i informacji o stacjach. **SQLink API** korzysta z istniejącego API SQLink. **None — local TG numbers** pokazuje lokalnie skonfigurowane TG i nie pobiera danych SQLink. Fala domyślnie używa None; jej API wymaga osobnej integracji po udostępnieniu. W panelu można wpisać dowolny numer TG. Na PiTFT lista pochodzi z domyślnej i monitorowanych TG; przy pustej liście pozostaje pozycja Monitor (TG 0).

Nazwa faktycznie zastosowanego profilu jest widoczna na ekranie głównym i w nagłówku WWW. Wybranie pozycji do edycji nie zmienia aktywnego profilu.

## Pliki i uprawnienia

| Ścieżka na Pi | Zawartość |
| --- | --- |
| `/var/lib/sqlink-profiles/profiles.json` | Baza profili, **z hasłami**; root, tryb 600, katalog 700 |
| `/var/lib/sqlink-profiles/pending.json` | Prywatny dziennik transakcji, tylko podczas przełączania; umożliwia odtworzenie po przerwaniu procesu |
| `/var/lib/sqlink-profile-state/active.json` | Publiczne metadane zastosowanego profilu, bez loginu i hasła; tryb 644 |
| `/etc/svxlink/svxlink.conf` | Konfiguracja aktualnego połączenia; istniejące prawa zachowane |
| `/var/backups/sqlink-profiles/` | Prywatne kopie konfiguracji i bazy przed aktywacją/usunięciem; pliki 600 |
| `/usr/local/sbin/sqlink_profiles.py` | Operacje profili wykonywane przez helper jako root |
| `/etc/systemd/system/sqlink-profiles.service` | Zastosowanie domyślnego profilu przy rozruchu |

Baza nie jest szyfrowana: bezpieczeństwo opiera się na uprawnieniach systemowych. Kopie zawierające hasła i klucze nie należą do repozytorium ani publicznego obrazu SD. Publiczny plik stanu nie zawiera danych uwierzytelniających.

## Integracja i aktualizacja

PiTFT i WWW korzystają z tego samego socketu helpera Wi-Fi. Akcje: `profiles_snapshot`, `profiles_save`, `profiles_activate`, `profiles_default`, `profiles_delete`. Zapis wymaga aktualnej rewizji, co chroni przed nadpisaniem zmian z drugiego interfejsu. Web API `/api/profiles` używa istniejącej sesji; POST wymaga CSRF. Stary zapis `user_save` jest zablokowany, aby nie omijał bazy profili.

Do instalacji potrzebne są pliki wymienione w `software/profiles-release.json`, istniejący helper, standardowe zależności Python/Pillow i systemd. Włącz `sqlink-profiles.service` po wgraniu modułów i wykonaniu migracji. Nie kopiuj całego rootfs na istniejące urządzenie: `server.py` w repozytorium ma przykładowy filtr sieci LAN.

`software/manifest.json` zachowuje pochodzenie pierwszego eksportu; `software/profiles-release.json` zawiera sumy tej aktualizacji. Obraz alpha-1 nie został przebudowany i nie zawiera profili.

## Sprawdzenia wykonane 22 września 2026

- 12 testów backendu: import bez ujawniania haseł, niezależność danych Fali, walidacja, niepełny profil, rewizje, usuwanie, PTT/RX, przełączanie, przywrócenie po nieudanym połączeniu, domyślny profil i zachowanie pozostałej konfiguracji.
- 3 testy UI/API: renderowanie ekranów PiTFT, klawiatura/nawigacja/anulowanie i brak pobierania API SQLink dla Fali.
- Symulacja WWW: lista, zablokowane działania, edycja i zapis, pomijanie pustego hasła, dodawanie i układ mobilny.
- Na prototypie: import SQLink, profil Fala bez danych, zapis/usunięcie tymczasowego profilu, odrzucenie aktywacji niepełnego profilu, renderowanie menu, ochrona HTTP 401 i aktywne usługi. Konfiguracja SvxLink i jego PID pozostały niezmienione podczas wdrożenia.
- Podczas końcowego sprawdzenia profil Fala był już uzupełniony i aktywny; lokalny stan SvxLink potwierdził połączenie. Domyślnym na rozruch nadal pozostawał SQLink. Nie eksportowano nowych danych logowania.
- Do sprawdzenia pozostają audio i TG Fali, powrót do SQLink, fizyczne przyciski oraz rozruch z innym profilem domyślnym.

Testy: `python3 software/tests/test_profiles.py`, `python3 software/tests/test_profiles_ui.py`. Pythonowe testy menu wymagają Pillow i czcionki DejaVu (Linux) lub Arial (macOS).

## Przywracanie poprzedniej wersji

Przed ręcznym odtwarzaniem zwolnij PTT i poczekaj na koniec RX. Zachowaj dodatkową kopię bieżącej bazy, jeśli po wdrożeniu dodano konta. Zatrzymaj panel, ekran i helper Wi-Fi, wyłącz usługę `sqlink-profiles.service`, odtwórz poprzednie wersje plików objętych aktualizacją z backupu kodu i wykonaj daemon-reload. Jeżeli od wdrożenia przełączano profile, odtwórz też konfigurację SvxLink z odpowiadającego backupu prywatnego, zachowując właściciela i prawa. Uruchom potrzebne usługi i sprawdź połączenie. Nie usuwaj prywatnej bazy ani backupów podczas diagnozy. Ta procedura ręczna nie była wykonana na prototypie; automatyczne przywrócenie po nieudanej aktywacji sprawdzono w testach z atrapą połączenia.
