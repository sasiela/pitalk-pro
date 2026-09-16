# Sprzęt i połączenia

## Zestaw odniesienia

Lista opisuje użyty prototyp, a nie gwarantowane zamienniki. Wersja maszynowa: [parts.csv](parts.csv).

| Element | Ilość | Znane dane / do uzupełnienia |
| --- | ---: | --- |
| Raspberry Pi 3 Model B Rev 1.2 | 1 | Model potwierdzony odczytem systemu |
| Adafruit PiTFT 2.2″ 240×320 HAT | 1 | Cztery przyciski; overlay `pitft22` |
| Karta dźwiękowa USB Sabrent | 1 | Obudowa prototypu około 34×23×10 mm; dokładny numer produktu i identyfikator USB do zapisania |
| Boczny przycisk chwilowy | 1 | Typ PBS-110 zgodny wymiarami z prototypem; przed zakupem sprawdzić konkretny wariant |
| microSD | 1 | Obraz alpha wymaga minimum 8 GB; karta testowa osobna od działającej instalacji |
| Zewnętrzne zasilanie i kabel | 1 zestaw | Dokładny model zasilacza i sprawdzenie pracy pod obciążeniem do udokumentowania |
| Mikrofon i odsłuch USB lub zestaw Bluetooth | 1 tor | Brak kompletnej listy sprawdzonych modeli i okablowania audio |
| Śruby stożkowe M3×12 | 2 | Dolne mocowanie frontu |
| Nakrętki M3 | 2 | W prototypie 5 mm między płaskimi bokami, grubość 2 mm |
| Śruby M3×12 do LCD / dystanse | 4 śruby + 4 dystanse | Śruby potwierdzone przez autora; długość dystansów do zwymiarowania |
| Przewody PTT i izolacja | 2 × około 10 cm | Koszulki termokurczliwe na każdym lucie; klej na gorąco do zamocowania przycisku |
| Części drukowane | 10 | Korpus V32, front V38, 4 nakładki V11, 2 pokrętła, podstawa i antena |

## Połączenia

Poniższe numery to **BCM, nie kolejne numery fizycznych pinów złącza**. Tabela opisuje konfigurację oprogramowania. Nie zastępuje sprawdzonego schematu montażowego.

| BCM | Rola |
| --- | --- |
| 17 | Przycisk BACK na PiTFT |
| 22 | Przycisk UP na PiTFT |
| 23 | Przycisk DOWN na PiTFT |
| 27 | Przycisk ENTER na PiTFT |
| 26 | Wejście PTT, pull-up, aktywne LOW; programowy debounce 30 ms |
| 24 | Programowy sygnał squelch: HIGH oznacza idle, LOW aktywuje wejście SvxLink |

Przycisk PTT łączy **fizyczny pin 37 (GPIO26)** z **fizycznym pinem 39 (GND)** po wciśnięciu. Autor podał tę kolejność montażu, a [zdjęcie połączeń](../../photos/IMG_3615.jpeg) pokazuje luty zabezpieczone koszulkami. Pełny opis i źródło numeracji: [instrukcja montażu](ASSEMBLY.md#numeracja-i-kontrola-ptt). Powyższa tabela nadal używa numeracji BCM. Nie podłączaj wyjścia zewnętrznego radia do wejścia przycisku.

GPIO24 jest sterowane przez system jako `gpio536` w prototypie. Ta liczba zależy od mapowania GPIO w jądrze. Nie jest numerem fizycznego pinu. Nie przenoś jej bez sprawdzenia na inny model/system.

## Mechanika i dokumentacja zdjęciowa

Obowiązują [wersje STL i instrukcja montażu](../../README.pl.md). Najpierw wydrukuj jedną nakładkę i wykonaj przymiarkę. Pokrętła i antena są ozdobne; nie ma zintegrowanego akumulatora ani potwierdzonej obsługi enkoderów.

[Instrukcja montażu ze zdjęciami](ASSEMBLY.md) prowadzi od frontu, przez PTT, do zamknięcia obudowy. [Indeks zdjęć](../../photos/README.md) opisuje wszystkie 24 pliki. Ostatnie etapy zamknięcia obudowy są opisane według autora, ale nie mają jeszcze osobnych zdjęć. Wymiary dystansów i kompletny rysunek montażowy pozostają do uzupełnienia.
