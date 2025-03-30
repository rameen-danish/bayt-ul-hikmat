import sqlite3
import streamlit as st
import time

# Class to manage the library
class PersonalLibraryManager:
    def __init__(self, db_name="library.db"):
        """Initialize the database and create books table if not exists."""
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        """Create books table if it does not exist."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    genre TEXT NOT NULL,
                    read INTEGER NOT NULL CHECK(read IN (0,1))
                )
            """)
            conn.commit()

    def add_book(self, title, author, year, genre, read_status):
        """Add a new book to the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author, year, genre, read) VALUES (?, ?, ?, ?, ?)",
                           (title, author, year, genre, int(read_status)))
            conn.commit()

    def remove_book(self, title):
        """Remove a book from the database by title."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE title = ?", (title,))
            conn.commit()
            return cursor.rowcount > 0

    def search_book(self, query):
        """Search for books by title or author (case-insensitive)."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?",
                           (f"%{query.lower()}%", f"%{query.lower()}%"))
            return cursor.fetchall()

    def mark_as_read_unread(self, title):
        """Toggle read/unread status for a book."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT read FROM books WHERE title = ?", (title,))
            result = cursor.fetchone()
            if result:
                new_status = 1 - result[0]
                cursor.execute("UPDATE books SET read = ? WHERE title = ?", (new_status, title))
                conn.commit()
                return new_status
            return None

    def get_library(self):
        """Retrieve all books from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            return cursor.fetchall()

    def get_statistics(self):
        """Get statistics of books in the database."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM books WHERE read = 1")
            read_books = cursor.fetchone()[0]

            percentage_read = (read_books / total_books * 100) if total_books else 0
            return total_books, read_books, percentage_read

# Initialize library manager
manager = PersonalLibraryManager()

# Set page config
st.set_page_config(page_title="📚 Personal Library Manager", layout="wide")

# Display title
st.title("📚 Personal Library Manager")

# Tabs for Navigation
tabs = st.tabs(["🏠 Home", "➕ Add Book", "🔍 Search Book", "❌ Remove Book", "📊 Statistics", "🚪 Exit"])

# 🏠 Home Tab
with tabs[0]:
    st.subheader("Your Library 📚")
    books = manager.get_library()
    if books:
        for book in books:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.write(f"📖 **{book[1]}**")
            with col2:
                st.write(f"✍️ {book[2]}")
            with col3:
                st.write(f"📅 {book[3]}")
            with col4:
                st.write(f"🏷️ {book[4]}")
            with col5:
                if st.button(f"✅ {'Read' if book[5] else 'Unread'}", key=book[0]):
                    manager.mark_as_read_unread(book[1])
                    st.rerun()
    else:
        st.write("📌 No books in your library. Add some!")

# ➕ Add Book Tab
with tabs[1]:
    st.subheader("➕ Add a New Book")
    title = st.text_input("📖 Book Title")
    author = st.text_input("✍️ Author")
    year = st.number_input("📅 Year (4-digit)", min_value=1000, max_value=9999, step=1)
    genre = st.text_input("🏷️ Genre")
    read_status = st.checkbox("✅ Read")
    if st.button("Add Book"):
        if title and author and genre and 1000 <= year <= 9999:
            manager.add_book(title, author, year, genre, read_status)
            st.success(f"✅ '{title}' added successfully!")
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ Please fill all fields correctly!")

# 🔍 Search Book Tab
with tabs[2]:
    st.subheader("🔍 Search for a Book")
    query = st.text_input("Enter title or author")
    if query:
        results = manager.search_book(query)
        if results:
            for book in results:
                st.write(f"📖 **{book[1]}** | ✍️ {book[2]} | 📅 {book[3]} | 🏷️ {book[4]} | ✅ {'Read' if book[5] else 'Unread'}")
        else:
            st.warning("❌ No matching books found.")

# ❌ Remove Book Tab
with tabs[3]:
    st.subheader("❌ Remove a Book")
    title = st.text_input("Enter book title to remove")

    if st.button("Remove Book"):
        if title:
            book_removed = manager.remove_book(title)  # Check if book exists
            if book_removed:
                st.success(f"✅ '{title}' has been removed successfully!")
                time.sleep(2)  # Wait for 2 seconds
                st.rerun()  # Refresh UI
            else:
                st.error("❌ Book not found! Please enter a valid title.")
        else:
            st.error("❌ Please enter a valid title.")

# 📊 Statistics Tab
with tabs[4]:
    st.subheader("📊 Library Statistics")
    total_books, read_books, percentage_read = manager.get_statistics()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Books", total_books)
    with col2:
        st.metric("✅ Read Books", read_books)
    with col3:
        st.metric("📖 Completion Rate", f"{percentage_read:.1f}%")

    st.progress(percentage_read / 100)

# 🚪 Exit Tab
with tabs[5]:
    st.subheader("🚪 Exit the Application")

    if st.button("Exit"):
        st.warning("✅ Exiting application... Please close the browser tab.")
        st.stop()  # Stop the app execution
# Footer
st.markdown("<br><hr><center>Made with ❤️ by Rameen Rashid</center>", unsafe_allow_html=True)