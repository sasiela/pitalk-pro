# Protokół testu własnego egzemplarza

Skopiuj ten dokument do raportu dla konkretnego egzemplarza i wersji. Puste pola oznaczają brak testu, nie sukces. Używaj wyników PASS / FAIL / NIE TESTOWANO i dodaj dowód lub krótką obserwację. Nie zamieszczaj haseł, prywatnych kluczy, cookies ani nieoczyszczonych logów.

- Data:
- Wersja/commit kodu:
- Obraz i SHA-256 lub sposób instalacji:
- Model Pi i rewizja:
- Ekran / karta USB / zestaw BT:
- Zasilanie:
- Wersje STL:
- OS / kernel:

| Próba | Oczekiwany wynik | Wynik / obserwacja |
| --- | --- | --- |
| Oględziny i mechanika | Brak zwarć/uszkodzeń, przyciski nie zakleszczają się, dostęp do złączy | |
| Pierwszy rozruch | System startuje, konfiguracja kończy się czytelnym statusem | |
| Własna tożsamość | Własne hasło, hostname i nowe klucze; brak kont/danych autora | |
| Rozmiar partycji | Rootfs wykorzystuje docelową kartę zgodnie z planem | |
| Ekran i cztery przyciski | Poprawna orientacja, każde sterowanie odpowiada opisowi | |
| Display | Kolory, jasność i timeout działają oraz pozostają po restarcie | |
| LAN / Wi-Fi | Połączenie, adres i autoconnect po restarcie | |
| Nowa sieć Wi-Fi | Skan, wpisanie hasła, wybór profilu i profil domyślny | |
| WWW przez IP / nazwę | Dostęp w LAN, poprawne logowanie i odmowa błędnego hasła | |
| User / reflektor | Własne dane zapisują się; status odpowiada stanowi połączenia | |
| Wybór TG | Wybrana grupa odpowiada stanowi urządzenia i panelu | |
| Monitorowanie / RX | Odbiór, callsign i wskaźnik dla faktycznej transmisji | |
| USB audio | Mikrofon i odsłuch na zamierzonym urządzeniu, regulacja głośności | |
| Bluetooth audio | Parowanie, połączenie, właściwy profil i działanie po restarcie | |
| PTT — kontrola bez nadawania | Wejście stabilne, puszczenie zwalnia PTT, start z wciśniętym przyciskiem nie uzbraja nadawania | |
| PTT — uzgodniony test głosu | Kontrolowana próba z odbiorcą, wyraźny początek i koniec; bez pozostania TX | |
| Odsłuch WWW | USB/BT nadal grają lokalnie, osobna głośność przeglądarki, Stop działa | |
| Zmiana strony / wylogowanie | Strumień odsłuchu kończy się | |
| Utrata i powrót sieci | Czytelny status oraz udokumentowane zachowanie ponownego łączenia | |
| Dłuższa praca | Zapis czasu obserwacji, ewentualnych rozłączeń i ich przyczyn | |
| Ponowny start | Konfiguracja pozostaje, usługi/audio startują w poprawnej kolejności | |
| Własny backup i odtworzenie | Udokumentowana kopia i odtworzenie na osobnej karcie | |

Test PTT bez nadawania musi być zorganizowany tak, aby drugi proces nie uruchamiał równolegle toru TX. Szczegóły trybu `--dry-run` i usługi sprawdź przed testem. Nie uruchamiaj drugiego procesu zajmującego GPIO26 równocześnie z normalną usługą przycisku.

## Podsumowanie egzemplarza

- Zaliczone:
- Błędy i sposób odtworzenia:
- Niesprawdzone:
- Czy druga osoba odtworzyła urządzenie bez prywatnej pomocy autora:

## Panel Audio diagnostics

Według [instrukcji](../build/AUDIO-TESTS.md) sprawdź na USB i BT: słyszalny ton 2 s, miernik reagujący na mowę przez 8 s, Stop, automatyczne zakończenie, opuszczenie strony, blokadę podczas RX/PTT, wyciszony/brakujący sprzęt i zmianę routingu. Potwierdź, że lokalne audio SvxLink działa po teście i nie została zmieniona głośność. Nie używaj rzeczywistej transmisji jako automatycznego testu.

## Dopasowanie wejścia Bluetooth — poprawka 17 września 2026

PipeWire może nazwać wyjście `bluez_output.AA_BB_CC_DD_EE_FF.1`, a wejście `bluez_input.AA:BB:CC:DD:EE:FF`. Poprzedni wybór transportu oczekiwał podkreśleń i dodatkowego sufiksu także dla wejścia. Teraz dopasowuje znormalizowany adres urządzenia. Trzy testy regresji obejmują obie postacie BT i USB: `python3 software/tests/test_bt_pair.py`. Po zmianie sprawdź zarówno domyślne wejście, jak i źródło istniejącego strumienia SvxLink.

## Profile reflektorów

Według [instrukcji](../build/PROFILES.md) sprawdź tworzenie/edycję/usuwanie w obu interfejsach, maskowanie hasła, konflikt rewizji przy równoległej edycji, aktywację poprawnego konta, odtworzenie po błędnym koncie, blokadę PTT/RX oraz domyślny profil po restarcie. Potwierdź brak danych SQLink w Fali, zachowanie USB/BT i Wi-Fi oraz nazwę aktywnego profilu na ekranie. Pełny test Fali wymaga gotowego serwera i osobnego konta.
