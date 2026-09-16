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
