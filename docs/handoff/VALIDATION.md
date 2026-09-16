# Kontrola pakietu przekazania

16 września 2026.

- Eksport 46 plików kodu/usług z jawnej listy urządzenia; sumy kopii zgodne z manifestem eksportu.
- Składnia wszystkich 28 plików Python poprawna; kontrola bez uruchamiania modułów sprzętowych.
- Składnia plików JavaScript i skryptów shell poprawna.
- Symulacja konfiguracji nowego obrazu: PASS, pliki tymczasowe i zastąpione operacje systemowe.
- Sprawdzono wzorce kluczy prywatnych i przypisań sekretów; w kodzie nie znaleziono wskazanych wzorców. To kontrola ograniczona, nie pełny audyt bezpieczeństwa.
- LOCAL-ACCESS.md jest wykluczony przez Git i ma prawa 600.
- Zachowano istniejące STL, filmy i inne materiały; zmieniono README, dodając informacje o kodzie.
- Nie wdrażano zmian na urządzeniu i nie wykonano commit/push.

Automatyczna kontrola bezpieczeństwa odrzuciła pierwszą próbę eksportu ze względu na ryzyko pobrania tokenu PulseAudio. Zastosowano węższą jawną listę kodu i usług, bez plików domowych, cookies, profili i kluczy. Taki eksport zakończył się poprawnie. Konfigurację WirePlumber odtworzono jako przykład z zapisanej wcześniej poprawki.

Ograniczenia: testy statyczne nie potwierdzają działania na nowej instalacji. Obraz alpha nie przeszedł fizycznego rozruchu. Eksport ma przykładowy filtr LAN i nie jest przeznaczony do zbiorczego nadpisania istniejącego urządzenia.
