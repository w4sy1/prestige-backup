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
