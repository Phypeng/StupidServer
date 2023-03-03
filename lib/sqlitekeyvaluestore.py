import sqlite3


class KeyValueStore(dict):
    def __init__(self, filename=None):
        self.__conn = sqlite3.connect(filename, isolation_level=None)
        self.__conn.execute("CREATE TABLE IF NOT EXISTS kv (key text unique, value text)")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__conn.commit()

    def __del__(self):
        self.__conn.commit()
        self.__conn.close()

    def __len__(self):
        rows = self.__conn.execute('SELECT COUNT(*) FROM kv').fetchone()[0]
        return rows if rows is not None else 0

    def iterkeys(self, prefix='', case_sensitivity=False):
        c = self.__conn.cursor()
        c.execute("PRAGMA case_sensitive_like = %s" % ('1' if case_sensitivity else '0'))
        cmd = f'SELECT key FROM kv WHERE key LIKE "{prefix}%"'
        for row in c.execute(cmd):
            yield row[0]

    def itervalues(self, prefix='', case_sensitivity=False):
        c = self.__conn.cursor()
        c.execute("PRAGMA case_sensitive_like = %s" % ('1' if case_sensitivity else '0'))
        cmd = f'SELECT value FROM kv WHERE key LIKE "{prefix}%"'
        for row in c.execute(cmd):
            yield row[0]

    def iteritems(self, prefix='', case_sensitivity=False):
        c = self.__conn.cursor()
        c.execute("PRAGMA case_sensitive_like = %s" % ('1' if case_sensitivity else '0'))
        cmd = f'SELECT key, value FROM kv WHERE key LIKE "{prefix}%"'
        for row in c.execute(cmd):
            yield row[0], row[1]

    def keys(self, prefix='', case_sensitivity=False):
        return list(self.iterkeys(prefix, case_sensitivity))

    def values(self, prefix='', case_sensitivity=False):
        return list(self.itervalues(prefix, case_sensitivity))

    def items(self, prefix='', case_sensitivity=False):
        return list(self.iteritems(prefix, case_sensitivity))

    def insert(self, key, value):
        self.__conn.execute('INSERT INTO kv (key, value) VALUES (?,?)', (key, value))

    def __contains__(self, key):
        return self.__conn.execute('SELECT 1 FROM kv WHERE key = ?', (key,)).fetchone() is not None

    def __getitem__(self, key):
        item = self.__conn.execute('SELECT value FROM kv WHERE key = ?', (key,)).fetchone()
        if item is None:
            raise KeyError(key)
        return item[0]

    def __setitem__(self, key, value):
        self.__conn.execute('REPLACE INTO kv (key, value) VALUES (?,?)', (key, value))

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        self.__conn.execute('DELETE FROM kv WHERE key = ?', (key,))

    def __iter__(self):
        return self.iterkeys()
