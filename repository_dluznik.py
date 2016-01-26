# -*- coding: utf-8 -*-

import sqlite3
import sqlite3
from datetime import datetime

#
# sciezka polaczenia z baza danych
#
db_path = 'dluznik.db'

#
# Wyjatek uzywany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

#
# Model danych
#


class Dluznik():
    """Model pojedynczego dluznika
    """
    def __init__(self, id, imie, nazwisko, dlugi=[]):
        self.id = id
        self.imie = imie
        self.nazwisko = nazwisko
        self.dlugi = dlugi
        self.ilosc = sum([item.ilosc for item in self.dlugi])

    def __repr__(self):
        return "<Dluznik(id='%s', imie='%s', nazwisko='%s', ilosc='%s', items='%s')>" % (
                    self.id, self.imie, self.nazwisko, str(self.ilosc), str(self.dlugi)
                )




class Dlug():
    """Model dlugu. Wystepuje tylko wewnatrz obiektu Dluznik.
    """
    def __init__(self, nazwa, ilosc):
        self.nazwa = nazwa
        self.ilosc = ilosc
        
    def __repr__(self):
        return "<Dlug(nazwa='%s', ilosc='%s')>" % (
                    self.nazwa, str(self.ilosc)
                )


#
# Klasa bazowa repozytorium
#
class Repository():


    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejscie do with ... as ...
    def __enter__(self):
        return self

    # wyjscie z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow typu Dluznik
#
class DluznikRepository(Repository):

    def add(self, dluznik):
        """Metoda dodaje pojedynczego dluznika do bazy danych,
        wraz ze wszystkimi jego dlugami.
        """
        try:
            c = self.conn.cursor()
            # zapisz dluznika
            ilosc = sum([item.ilosc for item in dluznik.dlugi])
            c.execute('INSERT INTO Dluznik (id, imie, nazwisko, ilosc) VALUES(?,?,?,?)',(dluznik.id,dluznik.imie,dluznik.nazwisko,dluznik.ilosc))

            # zapisz dlugi dluznika
            if dluznik.dlugi:
                for dlug in dluznik.dlugi:
                    try:
                        c.execute('INSERT INTO Dlugi (nazwa, ilosc, dluznik_id) VALUES(?,?,?)',
                                        (dlug.nazwa, dlug.ilosc, dluznik.id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding dluznik item: %s, to dluznik: %s' %
                                                  (str(dlug), str(dluznik.id)))
        except Exception as e:
            #print "dluznik add error:", e
            raise RepositoryException('error adding dluznik %s' % str(dluznik))

    def delete(self, dluznik):
        """Metoda usuwa pojedynczego dluznika z bazy danych,
        wraz ze wszystkimi jego dlugami.
        """
        try:
            c = self.conn.cursor()
            # usun pozycje
            c.execute('DELETE FROM Dlugi WHERE dluznik_id=?', (dluznik.id,))
            # usun naglowek
            c.execute('DELETE FROM Dluznik WHERE id=?', (dluznik.id,))

        except Exception as e:
            #print "dluznik delete error:", e
            raise RepositoryException('error deleting dluznik %s' % str(dluznik))

    def getById(self, id):
        """Get dluznik by id
        """
        try:
            c = self.conn.cursor()
            c.execute('SELECT * FROM Dluznik WHERE id=?', (id,))
            dl_row = c.fetchone()
            dluznik = Dluznik(id=id, imie=dl_row[1], nazwisko=dl_row[2] )
            if dl_row == None:
                dluznik=None
            else:
                dluznik.imie = dl_row[1]
                dluznik.nazwisko = dl_row[2]
                dluznik.ilosc = dl_row[3]
                c.execute("SELECT * FROM Dlugi WHERE dluznik_id=? ORDER BY 'nazwisko'", (id,))
                dl_items_rows = c.fetchall()
                items_list = []
                for item_row in dl_items_rows:
                    item = Dlug(nazwa=item_row[0], ilosc=item_row[1])
                    items_list.append(item)
                dluznik.dlugi=items_list
        except Exception as e:
            raise RepositoryException('error getting by id dluznik_id %s' % str(id))
        return dluznik

    def update(self, dluznik):
        """Metoda uaktualnia pojedynczego dluznika w bazie danych,
        wraz ze wszystkimi jego dlugami.
        """
        try:
            # pobierz z bazy dluznika
            dl_oryg = self.getById(dluznik.id)
            if dl_oryg != None:
                # dluznik jest w bazie: usun go
                self.delete(dluznik)
            self.add(dluznik)

        except Exception as e:
            #print "dluznik update error:", e
            raise RepositoryException('error updating dluznik %s' % str(dluznik))

if __name__ == '__main__':
    try:
        with DluznikRepository() as dluznik_repository:
            dluznik_repository.add(
                Dluznik(id = 1, imie = "Jan", nazwisko = "Kowalski",
                        dlugi = [
                            Dlug(nazwa = "kredyt hipoteczny",   ilosc = 200000),
                            Dlug(nazwa = "karta kredytowa",    ilosc = 300),
                        ]
                    )
                )
            dluznik_repository.complete()
    except RepositoryException as e:
        print(e)

if __name__ == '__main__':
    try:
        with DluznikRepository() as dluznik_repository:
            dluznik_repository.add(
                Dluznik(id = 2, imie = "Zygmunt", nazwisko = "Nowak",
                        dlugi = [
                            Dlug(nazwa = "kredyt hipoteczny",   ilosc = 154600),
                            Dlug(nazwa = "faktura",    ilosc = 1500),
                        ]
                    )
                )
            dluznik_repository.complete()
    except RepositoryException as e:
        print(e)

if __name__ == '__main__':
    try:
        with DluznikRepository() as dluznik_repository:
            dluznik_repository.add(
                Dluznik(id = 3, imie = "Elżbieta", nazwisko = "Ogonek",
                        dlugi = [
                            Dlug(nazwa = "leasing",   ilosc = 37250),
                        ]
                    )
                )
            dluznik_repository.complete()
    except RepositoryException as e:
        print(e)

if __name__ == '__main__':
    try:
        with DluznikRepository() as dluznik_repository:
            dluznik_repository.add(
                Dluznik(id = 4, imie = "Marcin", nazwisko = "Kowal",
                        dlugi = [
                            Dlug(nazwa = "pożyczka",   ilosc = 3400),
                            Dlug(nazwa = "zakupy ratalne",   ilosc = 2000),
                            Dlug(nazwa = "faktury",   ilosc = 300),
                        ]
                    )
                )
            dluznik_repository.complete()
    except RepositoryException as e:
        print(e)


print (DluznikRepository().getById(4))


    #
    #aktualizacja danych dluznika
    #
try:
    with DluznikRepository() as dluznik_repository:
         dluznik_repository.update(
             Dluznik(id = 4, imie = "Marcin", nazwisko = "Kowal",
                     dlugi = [
                         Dlug(nazwa = "pożyczka", ilosc = 3000),
                         Dlug(nazwa = "zakupy ratalne",   ilosc = 2100),
                         Dlug(nazwa = "faktury",   ilosc = 400),
                     ]
                 )
             )
         dluznik_repository.complete()
except RepositoryException as e:
    print(e)

print(DluznikRepository().getById(4))

    #
    #usuwanie danych dluznika
    #
#try:
#    with DluznikRepository() as dluznik_repository:
#        dluznik_repository.delete( Dluznik(id = 4, imie = "Marcin", nazwisko = "Kowal") )
#        dluznik_repository.complete()
#except RepositoryException as e:
#    print(e)
