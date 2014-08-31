import sqlite3

class PaintDB:
    p_tname = 'paintings'
    p2a_tname = 'paintings_to_awards'
    a_tname = 'awards'
    m_tname = 'misc'

    def table_exists(self, tname):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [tname])
        return not self.c.fetchone() == None

    def __init__(self, reset_paintings):
        self.conn = sqlite3.connect('kee.db')
        self.c = self.conn.cursor()

        if not self.table_exists(self.p2a_tname):
            self.c.execute("CREATE TABLE {0} (p_id int, a_id int)".format(self.p2a_tname))
            self.c.execute("CREATE TABLE {0} (description text)".format(self.a_tname))
            self.c.execute("""
                CREATE TABLE {0} (p_id int, quantity int, price int, comment text)
                """.format(self.m_tname))
            self.conn.commit()

        if reset_paintings:
            #p_backup = self.p_tname + "_backup"
            #self.c.execute("DROP TABLE IF EXISTS {0}".format(p_backup))
            #self.c.execute("ALTER TABLE {0} RENAME TO {1}".format(self.p_tname, p_backup))
            self.c.execute("DROP TABLE IF EXISTS {0}".format(self.p_tname))
            self.conn.commit()

        if not self.table_exists(self.p_tname):
            self.c.execute("CREATE TABLE {0} (full_url text, title text, thumb_img text, full_img text)".
                    format(self.p_tname))
            self.conn.commit()

    def paint_exists(self, link):
        self.c.execute("select * from {0} where full_url=?".format(self.p_tname), [link])
        return not self.c.fetchone() == None

    def add_paint(self, link_to_full, title, thumb_file, full_file):
        self.c.execute("insert into {0} values (?, ?, ?, ?)".format(self.p_tname),
                (link_to_full, title, thumb_file, full_file))
        self.conn.commit()

