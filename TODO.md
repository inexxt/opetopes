TODO licencjat:
 OK - horn filling
 OK - różne produkty 
 OK  - (09 x 09) - więcej niż 4
 OK  - (11 x 11)
 OK - przy konstrukcji, uważać żeby nie dodawać nic więcej (nic co się po rzutowaniu nie zawiera w P i Q)
 - zaczekać na wynik sprawdzenia, czy końcowa weryfikacja rzutowań jest potrzebna (tzn mamy już, że się zawiera, ale czy wypełnia całość)
 - nie liczyć dwa razy tych samych kształtów
 - wyczyszczenie kodu
 WIP - poprawnie skryptów konwersji z plików wejsciowych
 - normalne używanie
 - przerobić program tak, żeby Opetope i Face dziedziczyły po tuple (były immutable) i obok tego metody na match i verify


Optymalizacje:
 OK, 100x - all_subopetopes, all_subouts i to_string są atrybutami, a nie liczą wszystko od początku
 OK, ?x - doklejanie tylko tych, które się rzutują na P i Q
 OK, 2x - przetestować pypy - pypy3 3,78s, python3 7,24s (na 7_7.yaml)

FIXME ALARM - Opetop jest modyfikowany z powodu "abecadło problem"



