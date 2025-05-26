import oracledb

def get_connection():
    connection = oracledb.connect(
        user="S25_km242",       # <- change to your credentials
        password="uc38wTKk",
        dsn="oracle2.wiu.edu:1521/orclpdb1"              # <- e.g., "localhost/orclpdb"
    )
    return connection

def get_user_by_name(first_name, last_name):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT MemberID AS ID, FirstName, LastName, 'member' AS Role
    FROM LibraryMembers
    WHERE FirstName = :first AND LastName = :last
    UNION
    SELECT LibrarianID AS ID, FirstName, LastName,
           CASE WHEN Role = 'Admin' THEN 'admin' ELSE 'librarian' END AS Role
    FROM Librarians
    WHERE FirstName = :first AND LastName = :last
    """

    cursor.execute(sql, {"first": first_name, "last": last_name})
    result = cursor.fetchone()
    conn.close()
    return result