# Testowanie audio w panelu WWW

Otwórz `https://pitalk-pro.local:8443/#audio` i zaloguj się kontem systemowym `sqlink`.

1. Wybierz USB audio card lub Bluetooth headset. Dla Bluetooth najpierw połącz urządzenie i wybierz profil zapewniający mikrofon.
2. W razie potrzeby ustaw osobno Output device / Input microphone w Advanced routing i zatwierdź odpowiednim Apply. Wybrana pozycja listy nie zmienia routingu do chwili zatwierdzenia.
3. Ustaw wygodną głośność. W Audio diagnostics wybierz **Test speaker · 2 s**. Ton 660 Hz zabrzmi na fizycznym urządzeniu, a nie w przeglądarce. Test nie zmienia głośności urządzenia; własny strumień ma ograniczony poziom. Komunikat zakończenia potwierdza odtworzenie strumienia, słyszalność potwierdza użytkownik.
4. Wybierz **Test microphone · 8 s** i mów do mikrofonu bez naciskania PTT. Pasek pokazuje RMS od −60 do 0 dBFS. Wartość −60 obejmuje również sygnały poniżej tego progu. Bardzo niski poziom podczas ciszy jest normalny. Wynik „Signal detected” potwierdza obecność sygnału, nie zrozumiałość mowy ani odbiór przez reflektor.
5. **Stop test** przerywa test. Opuszczenie Audio lub wylogowanie również zleca zatrzymanie. Niezależny limit po stronie urządzenia kończy test także przy utracie połączenia z przeglądarką.

Test nie włącza PTT, nie zapisuje mikrofonu i nie przesyła próbek mikrofonu do przeglądarki. Zwracane są jedynie wartości poziomu. USB i Bluetooth korzystają z tego samego mechanizmu PipeWire/PulseAudio. Wyjście i wejście nie są przejmowane na wyłączność; SvxLink zachowuje swój tor audio.

Test jest blokowany przy RX/PTT lub niedostępnym stanie radia. Pojawienie się aktywności podczas testu powoduje jego przerwanie. Jest to kontrola programowa, nie sprzętowa blokada PTT — nie naciskaj PTT w celu testowania tonu. Zmiana domyślnego routingu kończy test przy kolejnym sprawdzeniu. W danej chwili może działać tylko jeden test, a zatrzymać go przez API może sesja, która go uruchomiła.

## Zależności i wdrażanie

Moduł `/opt/sqlink-web/audio_test.py`, `paplay`, `parec`, `pactl` i dostęp usługi panelu do socketu PulseAudio. Korzysta z istniejącego bind mount i `PULSE_SERVER`; nie wymaga nowych uprawnień. API GET/POST `/api/audio-test` wymaga sesji, POST także CSRF. Modyfikacja nie zmienia konfiguracji SvxLink ani zapisanych urządzeń.

## Weryfikacja 17 września 2026

- 9 testów logiki: poziom sygnału, blokada RX/PTT, walidacja urządzenia, wyciszenie, właściciel zadania, anulowanie, zmiana routingu, limit mikrofonu i brak próbek.
- 5 testów HTTP: brak sesji, CSRF, status, nieobsługiwana akcja i start/stop.
- Symulacja przeglądarki: wskaźnik, przyciski, Stop, opuszczenie widoku, szerokość telefonu i brak błędów JS.
- Prototyp USB: odczyt mikrofonu przez 8 sekund (niski poziom podczas sprawdzenia), proces odtwarzania tonu zakończony kodem 0; PTT pozostał nieaktywny. Test wykonano z konta i w przestrzeni montowań usługi panelu.
- Do potwierdzenia przez użytkownika: słyszalność tonu, reakcja na mowę i rzeczywisty test zestawu Bluetooth. Nie przełączano używanego sprzętu na BT podczas wdrożenia.

Lokalnie: `python3 software/tests/test_audio_test.py` oraz `python3 software/tests/test_http.py`. Test HTTP otwiera tymczasowy port localhost i korzysta z atrap, nie steruje radiem. Obraz alpha-1 nie został przebudowany i nie zawiera tej aktualizacji.
