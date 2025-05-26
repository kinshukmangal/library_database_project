from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from utils.db import get_connection
from utils.notifications import get_notifications, clear_notifications
from utils.audit import log_action

member_bp = Blueprint("member", __name__)

from utils.notifications import get_notifications, clear_notifications

from utils.notifications import get_notifications, clear_notifications

def load_member_notifications():
    user = session.get("user", {})
    if user.get("role") == "member":
        member_id = user.get("user_id")
        role = "member"
        flashed = session.get("flashed_notifications", [])

        # Load shelve-based messages for member
        shelve_msgs = get_notifications(member_id, role)
        for msg in shelve_msgs:
            if msg not in flashed:
                flashed.append(msg)

        # Load session flash messages
        flashed_messages = session.pop('_flashes', [])
        for _, msg in flashed_messages:
            if msg not in flashed:
                flashed.append(msg)

        session["flashed_notifications"] = flashed

        # Clear shelve-based ones after loading
        clear_notifications(member_id, role)

# ✅ Dashboard
@member_bp.route("/", endpoint="dashboard")
def dashboard():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()
    return render_template("member.html", name=session["user"]["first_name"])

# ✅ View available books
@member_bp.route("/view-books", endpoint="view_books")
def view_books():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT BookID, Title, Author, Genre, BookType, AvailableCopies, BranchID
        FROM Books
        WHERE AvailableCopies > 0 AND IsActive = 1
    """)
    rows = cursor.fetchall()
    columns = [desc[0].lower() for desc in cursor.description]
    books = [dict(zip(columns, row)) for row in rows]
    conn.close()

    return render_template("member_view_books.html", books=books)

# ✅ Book Search
@member_bp.route("/search-books")
def search_books():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")

    load_member_notifications()

    query = request.args.get("query", "").strip()
    filter_by = request.args.get("filter_by", "title")

    if not query:
        flash("Please enter a search term.")
        return redirect(url_for("member.view_books"))

    conn = get_connection()
    cursor = conn.cursor()

    if filter_by == "bookid" and query.isdigit():
        cursor.execute("""
            SELECT BookID, Title, Author, Genre, BookType, AvailableCopies, BranchID
            FROM Books
            WHERE BookID = :1 AND IsActive = 1
        """, (int(query),))
    elif filter_by == "author":
        cursor.execute("""
            SELECT BookID, Title, Author, Genre, BookType, AvailableCopies, BranchID
            FROM Books
            WHERE LOWER(Author) LIKE :1 AND IsActive = 1
        """, (f"%{query.lower()}%",))
    else:  # title
        cursor.execute("""
            SELECT BookID, Title, Author, Genre, BookType, AvailableCopies, BranchID
            FROM Books
            WHERE LOWER(Title) LIKE :1 AND IsActive = 1
        """, (f"%{query.lower()}%",))

    rows = cursor.fetchall()
    columns = [desc[0].lower() for desc in cursor.description]
    books = [dict(zip(columns, row)) for row in rows]
    conn.close()

    return render_template("member_view_books.html", books=books)

# ✅ QR Code Scanner
@member_bp.route("/scan-qr")
def scan_qr():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()
    return render_template("member_scan_qr.html")

# ✅ Member Loans
@member_bp.route("/my-loans")
def my_loans():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT L.LoanID, B.Title, L.LoanDate, L.DueDate, L.ReturnDate, L.Status, L.FineAmount
        FROM Loans L
        JOIN Books B ON L.BookID = B.BookID
        WHERE L.MemberID = :1 AND B.IsActive = 1
    """, (session["user"]["user_id"],))
    loans = cursor.fetchall()
    conn.close()

    return render_template("member_loans.html", loans=loans)

# ✅ Member Reservations
@member_bp.route("/my-reservations")
def my_reservations():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.TransactionID, B.Title, T.TransactionDate, T.Status
        FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        WHERE T.MemberID = :1 AND T.TransactionType = 'Reservation' AND B.IsActive = 1
    """, (session["user"]["user_id"],))
    reservations = cursor.fetchall()
    conn.close()

    return render_template("member_reservations.html", reservations=reservations)

# ✅ Cancel Reservation
@member_bp.route("/cancel-reservation/<int:transaction_id>")
def cancel_reservation(transaction_id):
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")

    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Transactions
        SET Status = 'Cancelled'
        WHERE TransactionID = :1 AND MemberID = :2 AND Status = 'Pending'
    """, (transaction_id, session["user"]["user_id"]))

    conn.commit()
    conn.close()
    flash("❌ Reservation request canceled.")
    return redirect("/member/my-reservations")

# ✅ Member Transactions
@member_bp.route("/my-transactions")
def my_transactions():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.TransactionID, B.Title, T.TransactionType, T.Amount, T.TransactionDate, T.Status
        FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        WHERE T.MemberID = :1 AND B.IsActive = 1
    """, (session["user"]["user_id"],))
    transactions = cursor.fetchall()
    conn.close()

    return render_template("member_transactions.html", transactions=transactions)

# ✅ Member Fines
@member_bp.route("/my-fines")
def my_fines():
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.TransactionID, B.Title, T.Amount, T.Status
        FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        WHERE T.MemberID = :1 AND T.TransactionType = 'Fine Payment' AND T.Status = 'Pending' AND B.IsActive = 1
    """, (session["user"]["user_id"],))
    fines = cursor.fetchall()
    conn.close()

    return render_template("member_fines.html", fines=fines)

@member_bp.route("/reserve/<int:book_id>")
def reserve_book(book_id):
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(TransactionID) FROM Transactions")
    last_id = cursor.fetchone()[0] or 5000
    new_id = last_id + 1

    cursor.execute("""
        INSERT INTO Transactions (
            TransactionID, MemberID, BookID, TransactionType, TransactionDate, Status
        ) VALUES (
            :1, :2, :3, 'Reservation', SYSDATE, 'Pending'
        )
    """, (new_id, session["user"]["user_id"], book_id))

    log_action(session["user"]["user_id"], "Member", f"Requested reservation for BookID {book_id}")

    conn.commit()
    conn.close()
    flash("📌 Reservation request submitted.")
    return redirect("/member/view-books")

@member_bp.route("/checkout/<int:book_id>")
def checkout_book(book_id):
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
    load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()

    # Check if book is available and active
    cursor.execute("""
        SELECT AvailableCopies, IsActive FROM Books WHERE BookID = :1
    """, (book_id,))
    row = cursor.fetchone()

    if not row or row[0] < 1 or row[1] == 0:
        flash("⚠️ This book is not available or has been removed.")
        return redirect("/member/view-books")

    # Create a transaction for checkout
    cursor.execute("SELECT MAX(TransactionID) FROM Transactions")
    max_tid = cursor.fetchone()[0] or 5000
    new_tid = max_tid + 1

    cursor.execute("""
        INSERT INTO Transactions (TransactionID, MemberID, BookID, TransactionType, TransactionDate, Status)
        VALUES (:1, :2, :3, 'Checkout', SYSDATE, 'Completed')
    """, (new_tid, session["user"]["user_id"], book_id))

    # Create a loan
    cursor.execute("SELECT MAX(LoanID) FROM Loans")
    max_lid = cursor.fetchone()[0] or 4000
    new_lid = max_lid + 1

    cursor.execute("""
        INSERT INTO Loans (LoanID, MemberID, BookID, LoanDate, DueDate, Status)
        VALUES (:1, :2, :3, SYSDATE, SYSDATE + 14, 'Borrowed')
    """, (new_lid, session["user"]["user_id"], book_id))

    # Decrease AvailableCopies
    cursor.execute("""
        UPDATE Books SET AvailableCopies = AvailableCopies - 1 WHERE BookID = :1
    """, (book_id,))

    conn.commit()
    conn.close()
    flash("✅ Book checked out successfully!")
    return redirect(url_for("book.view_book", book_id=book_id))

# ✅ Member Return Book (Request)
@member_bp.route("/return-book/<int:book_id>")
def return_book(book_id):
    if session.get("user", {}).get("role") != "member":
        return redirect("/login")
        load_member_notifications()

    conn = get_connection()
    cursor = conn.cursor()

    # Create return transaction
    cursor.execute("SELECT MAX(TransactionID) FROM Transactions")
    last_tid = cursor.fetchone()[0] or 5000
    new_tid = last_tid + 1

    cursor.execute("""
        INSERT INTO Transactions (
            TransactionID, MemberID, BookID, TransactionType,
            TransactionDate, Status
        ) VALUES (
            :1, :2, :3, 'Return', SYSDATE, 'Pending'
        )
    """, (new_tid, session["user"]["user_id"], book_id))

    log_action(session["user"]["user_id"], "Member", f"Requested return for BookID {book_id}")

    conn.commit()
    conn.close()
    flash("🔄 Return request submitted.")
    return redirect(url_for("book.view_book", book_id=book_id))