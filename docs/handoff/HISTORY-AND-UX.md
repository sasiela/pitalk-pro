# Historia decyzji i preferencje

To chronologia funkcjonalna z dostępnego kontekstu; aktualny kod ma pierwszeństwo przed wcześniejszymi prośbami o wygląd.

## Urządzenie

Na początku pomylono płytki. Model potwierdzony z systemu to Raspberry Pi 3 Model B Rev 1.2. Brak Wi-Fi rozwiązano przez utworzenie profilu NetworkManager. Następnie uruchomiono trwały PTT, osobną usługę przycisku i bezpieczny stan GPIO24.

## Menu PiTFT

- Właściciel wybrał wpisywanie danych przyciskami przez klawiaturę ekranową.
- Wi-Fi: skan, dodawanie sieci, wybór zapisanej, profil domyślny/autoconnect.
- Menu ujednolicono kolorystycznie. Tytuły zmniejszono, dopasowano położenie i linie oddzielające zawartość.
- Na ekranie głównym usunięto datę na rzecz oznaczenia MENU.
- Fizyczne przyciski są po lewej: ikona BACK u góry po lewej, pozostałe oznaczenia u dołu. Dodatkowe przesunięcie ikon o 4 px zostało później cofnięte.
- Na ekranie głównym BACK i UP miały być nieaktywne, DOWN prowadzić do wyboru Talk Groups. Faktyczne mapowanie sprawdzaj w końcowej pętli `sqlink-screen.py`.
- Powrót po bezczynności początkowo 10 s, potem 30 s; obecnie wartość jest ustawieniem Display. Nie nadpisuj jej globalną stałą.
- Display: Brightness w procentach, schemat kolorów i idle timeout; zapis między restartami.
- Restart: osobne menu kontroli restartu.
- Bluetooth: skanowanie, parowanie i wybór urządzenia, połączenie/rozłączenie oraz opcje audio; stan przez helper.
- Audio: USB lub Bluetooth oraz Volume. Zmianę głośności poprawiono tak, aby każde UP/DOWN nie wywoływało blokującego ekranu „Reading audio”.
- User: login/callsign i hasło reflektora, grupa domyślna, monitorowane grupy oraz zapis z ponownym połączeniem.

## Ekran główny

ONLINE jest zielone, OFFLINE czerwone. Status pracy MONITOR/RX/TX jest odrębny od połączenia. Podczas RX pokazuje się callsign nadawcy, większy i w niebieskim kolorze, wyśrodkowany między nazwą grupy a statusem. Numer TG zmniejszono; nazwa grupy jest bezpośrednio pod nim. Pasek poziomu audio odświeża się szybciej podczas odbioru, bez kosztownego pełnego odczytu stanu na każdej klatce.

## Panel WWW

Najpierw rozważano brak hasła, ale końcowa decyzja właściciela to logowanie systemowym kontem `sqlink` i jego hasłem. Zachowaj uwierzytelnianie. Panel otrzymał aktywność TG, listy stacji, popup po callsign, zarządzanie urządzeniem i odsłuch.

Odsłuch WWW miał zachować dźwięk na fizycznym urządzeniu, działać dla USB i Bluetooth oraz mieć niezależną głośność przeglądarki. Nie jest funkcją nadawania z mikrofonu przeglądarki.

## Prezentacje i inne rozmowy

Przygotowywano filmy panelu i fizycznego ekranu z polskimi napisami oraz syntetycznym lektorem. Pełny przegląd urządzenia obejmował 67 kroków. Tymczasowy mechanizm sterowania ekranem na potrzeby filmu został usunięty, a zwykła usługa przywrócona.

Rozmawiano też o własnym reflektorze, EuroLink/EchoLink i konferencjach EchoLink. W dostępnej historii nie ma potwierdzenia wdrożenia własnego serwera ani modułu EchoLink w tym projekcie. Nie przedstawiaj tych rozmów jako działających funkcji ani aktualnych ustaleń formalnych.

## Preferencje współpracy

Właściciel woli, aby asystent wykonywał zlecone zmiany sam, korzystając z dostępnego terminala/SSH. Nie chce ciągłego ponownego pytania o już uzgodnione czynności. Jednocześnie ważne są kopie, zachowanie danych logowania, brak ujawniania sekretów i jasna informacja, co sprawdzono. Opisy dla użytkownika po polsku, teksty produktu po angielsku.
