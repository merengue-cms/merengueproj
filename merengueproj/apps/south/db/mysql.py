
from django.db import connection
from django.conf import settings
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    MySQL implementation of database operations.
    """
    
    backend_name = "mysql"
    alter_string_set_type = ''
    alter_string_set_null = 'MODIFY %(column)s %(type)s NULL;'
    alter_string_drop_null = 'MODIFY %(column)s %(type)s NOT NULL;'
    drop_index_string = 'DROP INDEX %(index_name)s ON %(table_name)s'
    drop_primary_key_string = "ALTER TABLE %(table)s DROP PRIMARY KEY"
    allows_combined_alters = False
    has_ddl_transactions = False
    has_check_constraints = False
    delete_unique_sql = "ALTER TABLE %s DROP INDEX %s"
    
    
    def execute(self, sql, params=[]):
        if hasattr(settings, "DATABASE_STORAGE_ENGINE") and \
           settings.DATABASE_STORAGE_ENGINE:
            generic.DatabaseOperations.execute(self, "SET storage_engine=%s;" %
                settings.DATABASE_STORAGE_ENGINE)
        return generic.DatabaseOperations.execute(self, sql, params)
    execute.__doc__ = generic.DatabaseOperations.execute.__doc__

    
    def rename_column(self, table_name, old, new):
        if old == new or self.dry_run:
            return []
        
        qn = connection.ops.quote_name
        
        rows = [x for x in self.execute('DESCRIBE %s' % (qn(table_name),)) if x[0] == old]
        
        if not rows:
            raise ValueError("No column '%s' in '%s'." % (old, table_name))
        
        params = (
            qn(table_name),
            qn(old),
            qn(new),
            rows[0][1],
            rows[0][2] == "YES" and "NULL" or "NOT NULL",
            rows[0][3] == "PRI" and "PRIMARY KEY" or "",
            rows[0][4] and "DEFAULT " or "",
            rows[0][4] and "%s" or "",
            rows[0][5] or "",
        )
        
        sql = 'ALTER TABLE %s CHANGE COLUMN %s %s %s %s %s %s %s %s;' % params
        
        if rows[0][4]:
            self.execute(sql, (rows[0][4],))
        else:
            self.execute(sql)
    
    
    def delete_column(self, table_name, name):
        qn = connection.ops.quote_name
        db_name = settings.DATABASE_NAME
        
        # See if there is a foreign key on this column
        cursor = connection.cursor()
        get_fkeyname_query = "SELECT tc.constraint_name FROM \
                              information_schema.table_constraints tc, \
                              information_schema.key_column_usage kcu \
                              WHERE tc.table_name=kcu.table_name \
                              AND tc.table_schema=kcu.table_schema \
                              AND tc.constraint_name=kcu.constraint_name \
                              AND tc.constraint_type='FOREIGN KEY' \
                              AND tc.table_schema='%s' \
                              AND tc.table_name='%s' \
                              AND kcu.column_name='%s'"

        result = cursor.execute(get_fkeyname_query % (db_name, table_name, name))
        
        # if a foreign key exists, we need to delete it first
        if result > 0:
            assert result == 1 #we should only have one result
            fkey_name = cursor.fetchone()[0]
            drop_query = "ALTER TABLE %s DROP FOREIGN KEY %s"
            cursor.execute(drop_query % (qn(table_name), qn(fkey_name)))

        super(DatabaseOperations, self).delete_column(table_name, name)

    
    def rename_table(self, old_table_name, table_name):
        """
        Renames the table 'old_table_name' to 'table_name'.
        """
        if old_table_name == table_name:
            # No Operation
            return
        qn = connection.ops.quote_name
        params = (qn(old_table_name), qn(table_name))
        self.execute('RENAME TABLE %s TO %s;' % params)
    
    
    def _constraints_affecting_columns(self, table_name, columns, type="UNIQUE"):
        """
        Gets the names of the constraints affecting the given columns.
        """
        
        if self.dry_run:
            raise ValueError("Cannot get constraints for columns during a dry run.")
        
        columns = set(columns)
        db_name = settings.DATABASE_NAME
        # First, load all constraint->col mappings for this table.
        rows = self.execute("""
            SELECT kc.constraint_name, kc.column_name
            FROM information_schema.key_column_usage AS kc
            JOIN information_schema.table_constraints AS c ON
                kc.table_schema = c.table_schema AND
                kc.table_name = c.table_name AND
                kc.constraint_name = c.constraint_name
            WHERE
                kc.table_schema = %s AND
                kc.table_catalog IS NULL AND
                kc.table_name = %s AND
                c.constraint_type = %s
        """, [db_name, table_name, type])
        # Load into a dict
        mapping = {}
        for constraint, column in rows:
            mapping.setdefault(constraint, set())
            mapping[constraint].add(column)
        # Find ones affecting these columns
        for constraint, itscols in mapping.items():
            if itscols == columns:
                yield constraint
