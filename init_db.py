# -*- coding: utf-8 -*-

import sqlite3


db_path = 'dluznik.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute('''
          CREATE TABLE Dluznik
          ( id INTEGER PRIMARY KEY,
            imie VARCHAR(10) NOT NULL,
            nazwisko VARCHAR(15) NOT NULL,
	        ilosc NUMERIC NOT NULL
	  )
          ''')
c.execute('''
          CREATE TABLE Dlugi
          ( nazwa VARCHAR(100),
            ilosc NUMERIC NOT NULL,
            dluznik_id INTEGER,
           FOREIGN KEY(dluznik_id) REFERENCES Dluznik(id),
           PRIMARY KEY (ilosc, dluznik_id) )
          ''')
