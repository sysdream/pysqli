#-*- coding: utf-8 -*-

from exceptions import Unavailable, UnknownField

## Field wrapper
# This class is a simple wrapper for table's fields

class FieldWrapper:
    def __init__(self, dbms, table, db, field):
        self.dbms = dbms
        self.table = table
        self.db = db
        self.field = field        
    
    def __eq__(self, other):
        return (other == self.field)
    
    def __str__(self):
        return self.field
        
    def __repr__(self):
        return self.field


## Table wrapper
# This class is part of PySQLi "magic"
#
# It provides an interface to the injection framework, automating the reading and the analysis
# of a DBMS table's structure. This class provides a bunch of methods to query directly a given
# table:
#
#  - select(): allows multiple rows selection and field selection
#  - all(): dumps all the rows (generator, should be use in a for loop)
#  - describe(): describes the table's structure

class TableWrapper:
    
    
    ## Constructor
    # @param dbms DBMS Plugin object
    # @param table Table name
    # @param db Database name
    
    def __init__(self, dbms, table, db):
        self.dbms = dbms
        self.table = table
        self.db = db
        self.__fields = None
    
    
    ## Get all the fields of this table
    # @return List of FieldWrapper objects
    
    def fields(self):
        self.update()
        return self.__fields


    ## Update fields
    # Update fields if it has not been done. If it has already been done, do nothing except if force is set to True.
    # @param force Force update

    def update(self, force=False):
        if (self.__fields is None) or force:
            self.__fields = [f for f in self.dbms.fields(self.table,self.db)]

    ## Describe table's structure
    # Describe the table's structure in a string ready to be displayed
    # @return Table's desc string
    
    def describe(self):
        self.update()
        return "Table %s\n"%self.table+'\n'.join([' -> %s'%field for field in self.__fields])


    ## Count table's records
    # @return Table's cardinal
    
    def count(self):
        return self.dbms.count_table_records(self.table,self.db,1000000)


    ## Select some rows from the table
    # Select a given number of rows and given fields from a starting index
    #
    # @param pos Starting index
    # @param num Number of rows to select
    # @param fields List of fields (as string) to select
    # @return List of records, or single record if there is only one 
    
    def select(self, pos=0, num=1, fields=None):
        try:
            if fields is None:
                self.update()
        except Unavailable:
            if fields is not None:
                pass
            else:
                raise Unavailable()
                
        records = []
        for i in range(pos,pos+num):
            record = {}
            if fields is None:
                for field in self.__fields:
                    record[field] = self.dbms.get_record_field_value(field, self.table, i, self.db)
            else:
                for field in fields:
                    record[field] = self.dbms.get_record_field_value(field, self.table, i, self.db)                    
            records.append(record)
        return records

    ## Dump the whole table
    # This method is a generator and yield each record once dumped. Must be used in a for loop for
    # an efficiency purpose.
    #
    # @param fields Array of fields to retrieve. If not specified, all fields are retrieved
    # @return List of records

    def all(self, fields=None):
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


    ## Get database number of fields
    # @return Number of fields contained in this table

    def __len__(self):
        return self.dbms.get_nb_fields(self.table, self.db)

    ## Wrap a field for this 

    def __getitem__(self, key):
        return FieldWrapper(self.dbms, self.table, self.db, key)

    def __str__(self):
        return self.table

    def __repr__(self):
        return self.table
        
    def __eq__(self, other):
        return (self.table==other)


class DatabaseWrapper:
    def __init__(self, dbms, db):
        self.dbms = dbms
        self.db = db
        self.__tables = None
        
    def tables(self):
        if self.__tables is None:
            self.update()
        return self.__tables

    def update(self):
        self.__tables = self.dbms.tables(self.db)

    def __len__(self):
        return self.dbms.getNbTables(self.db)

    def __getitem__(self, key):
        return TableWrapper(self.dbms, key, self.db)

    def __str__(self):
        return self.db

    def __repr__(self):
        return self.db
