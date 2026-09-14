# Użycie

`python app.py plan --source C:/Users/USER/Documents --source C:/Users/USER/Pictures`
`python app.py backup --source ./dane --destination ./kopia --apply`
`python app.py verify --destination ./kopia`

Wskaż Desktop/Documents/Pictures/Downloads lub inne foldery ręcznie, także przekierowane
do OneDrive. Nie zakładamy stałych ścieżek. Źródła dostają oddzielne podkatalogi.
Filtry pomijają znane nazwy sekretów, profile aplikacji AppData, klucze i .git.
Nie analizują semantycznie zawartości dokumentów: sekret zapisany w zwykłym dokumencie
może zostać skopiowany. Przed backupem wybierz źródła i przejrzyj plan.
Bookmarks można przenieść do osobnego wybranego folderu; program nie kopiuje profilu przeglądarki.
MVP nie eksportuje jeszcze sterowników ani ustawień systemowych. Kopia jest plikowa,
bez VSS/ACL/ADS, szyfrowania, kompresji i automatycznego przywracania. Pliki otwarte mogą dać błąd.

## Rozszerzenia 0.2.0

`python app.py folders` pokazuje standardowe foldery użytkownika, także przekierowane w Windows.
`python app.py backup --standard-folder Documents --destination D:/Serwis/Kopia --apply`
Opcje `--system-export`, `--drivers` oraz powtarzane `--bookmarks "C:/.../Bookmarks"`
dołączają listę aplikacji/konfigurację, pakiety sterowników (pnputil, może wymagać administratora)
i oczyszczone drzewo zakładek Chromium. Nie kopiujemy całego profilu przeglądarki.
Zakładki usuwają login/hasło, query i fragment URL; tytuły i ścieżki nadal mogą być prywatne.
Wszystkie eksporty trafiają do manifestu SHA256. Niepowodzenie pozostawia niekompletny manifest.
`python app.py restore --destination D:/Serwis/Kopia --restore-to D:/Odtworzone` pokazuje plan.
Dodaj `--apply`, aby odtworzyć do NOWEGO katalogu. Kopia jest weryfikowana przed odtwarzaniem
oraz podczas kopiowania. Nic nie jest automatycznie instalowane ani importowane do systemu.
Filtry nazw nie wykrywają sekretów ukrytych w dowolnej treści dokumentów. Wskaż świadomie źródła.
