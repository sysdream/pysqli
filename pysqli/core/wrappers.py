#-*- coding: utf-8 -*-

"""
This module provides three wrappers, as an abstraction layer
of the exploited database. 

Classes:

    DatabaseWrapper
    TableWrapper
    FieldWrapper

"""

from exceptions import Unavailable


class FieldWrapper(object):
    """
    Database field/column abstraction layer.
    """

    def __init__(self, dbms, table, db, field):
        self.dbms = dbms
        self.table = table
        self.db = db
        self.field = field        
    
    def __eq__(self, other):
        return other == self.field
    
    def __str__(self):
        return self.field
        
    def __repr__(self):
        return self.field


class TableWrapper(object):

    """
    Database table abstraction layer.

    This wrapper provides methods to enumerate every field
    and extract data from a given table.
    """
    
    def __init__(self, dbms, table, db):
        """
        Constructor

        dbms: pysqli's dbms instance
        table: target table name
        db: wrapped database instance
        """
        self.dbms = dbms
        self.table = table
        self.db = db
        self.__fields = None
    
    
    def fields(self):
        """
        Retrieve all table's fields (wrapped)
        """
        self.update()
        return self.__fields


    def update(self, force=False):
        """
        Update fields info and cache.

        force: Force cache cleanup before updating.
        """
        if (self.__fields is None) or force:
            self.__fields = [f for f in self.dbms.fields(self.table, self.db)]

    def describe(self):
        """
        Describes table structure.
        """
        self.update()
        return "Table %s\n" % self.table + '\n'.join([' -> %s' % field for field in self.__fields])


    def count(self):
        """
        Count table's records.
        """
        return self.dbms.count_table_records(self.table,self.db,1000000)


    def select(self, start=0, count=1, fields=None):
        """
        Select rows

        start: start row index
        count: number of rows to return
        fields: list of fields to select (default: all)
        """
        try:
            if fields is None:
                self.update()
        except Unavailable:
            if fields is None:
                raise Unavailable()

        records = []
        for i in range(start, start + count):
            record = {}
            if fields is None:
                for field in self.__fields:
                    record[field] = self.dbms.get_record_field_value(field, self.table, i, self.db)
            else:
                for field in fields:
                    record[field] = self.dbms.get_record_field_value(field, self.table, i, self.db)                    
            records.append(record)
        return records

    def all(self, fields=None):
        """
        Enumerate all rows as a dictionary.

        fields: list of fields to select (default: all)
        """
        if fields is None:
            self.update()
        for i in range(self.count()):
            record = {}
            if fields is None:
                for field in self.__fields:
                    record[str(field)] = self.dbms.get_record_field_value(field, self.table, i, self.db)
            else:
                for field in fields:
                    record[field] = self.dbms.get_record_field_value(field, self.table, i, self.db)
            yield record    


    def __len__(self):
        """
        Retrieve the number of databases
        """
        return self.dbms.get_nb_fields(self.table, self.db)

    def __getitem__(self, key):
        """
        Retrieve field/column info

        key: field/column name
        """
        return FieldWrapper(self.dbms, self.table, self.db, key)

    def __str__(self):
        """
        Retrieve table's name
        """
        return self.table

    def __repr__(self):
        """
        Display table name
        """
        return self.table
        
    def __eq__(self, other):
        """
        Compares tables based on their names
        """
        return self.table == other


class DatabaseWrapper:
    """
    Database abstraction layer.
    """

    def __init__(self, dbms, db):
        self.dbms = dbms
        self.db = db
        self.__tables = None
        
    def tables(self):
        """
        Enumerate database's tables
        """
        if self.__tables is None:
            self.update()
        return self.__tables

    def update(self):
        """
        Update tables list
        """
        self.__tables = self.dbms.tables(self.db)

    def __len__(self):
        """
        Retrieve the number of tables present in the database
        """
        return self.dbms.getNbTables(self.db)

    def __getitem__(self, key):
        """
        Retrieve a wrapped table based on its name
        """
        return TableWrapper(self.dbms, key, self.db)

    def __str__(self):
        """
        Retrieve database name
        """
        return self.db

    def __repr__(self):
        """
        Display database name
        """
        return self.db

