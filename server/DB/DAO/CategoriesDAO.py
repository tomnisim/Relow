

class CategoriesDAO:

    def __init__(self, conn):
        self._conn = conn

    def insert(self, category):
        self._conn.execute("""INSERT INTO category (category_id,name) VALUES (?,?)""",
                           [category.id, category.name])
        self._conn.commit()


    def delete(self, category):
        self._conn.execute("""DELETE FROM category WHERE  category_id = ? """, [category.id])
        self._conn.commit()


    def update(self, category):
        self._conn.execute("""UPDATE category set name = ? where category_id = ?""",
                           [category.name, category.id])
        self._conn.commit()

    def load_category_id(self):
        this = self._conn.cursor()
        this.execute("SELECT MAX(category_id) FROM category")
        output = this.fetchone()[0]
        print(output)
        if output is None:
            output = 0

        return output + 1

    def get_all(self):
        this = self._conn.cursor()
        this.execute("SELECT * FROM  category")
        return this.fetchall()


