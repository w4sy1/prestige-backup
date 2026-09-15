# Błędy i przerwanie kopii

Manifest backupu pozostaje `complete: false` przez cały czas kopiowania,
eksportów i zapisu ACL. Dopiero zakończenie wszystkich etapów bez błędów
ustawia `complete: true`. Weryfikacja sprawdza hashe, rozmiary (jeżeli zapisano)
i błędy manifestu. Niespójny lub niekompletny backup nie może być odtworzony.

Przerwana kopia pozostaje w swoim katalogu. Program nie usuwa jej automatycznie
ani nie nadpisuje przy następnym uruchomieniu. Wybierz nowy katalog i ponów backup.

Odtwarzanie tworzy obok katalogu docelowego `prestige-restore-<id>.json`:

- `COMPLETE`: wszystkie pliki odtworzono i zweryfikowano, a żądane ACL zastosowano.
- `FAILED`: odnotowano błędy; sprawdź pole `errors`.
- `IN_PROGRESS`: operacja trwa albo została przerwana przed zapisaniem końcowego stanu.

Po przerwaniu najpierw sprawdź, czy proces nadal działa. Niedokończony katalog
może zawierać częściowe pliki. Ponów odtwarzanie do nowego katalogu; program
nie nadpisuje istniejącego. Nie ma automatycznego wznowienia w połowie pliku.
Oryginalny backup nie jest zmieniany przez restore.

Dziennik VSS jest osobny (`vss-<id>.json`). `vss-recover --vss-journal ...`
pokazuje plan sprzątania migawek, a `--apply` wykonuje go. Nie zastępuje to
ponownego wykonania niekompletnej kopii.
