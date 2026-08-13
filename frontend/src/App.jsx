import BookCRUD from "./components/BookCRUD";

export default function App() {
  return (
    <div className="app">
      <header>
        <h1>Bibliothèque</h1>
      </header>
      <main>
        <BookCRUD />
      </main>
      <footer>
        <p>Lova &copy; 2026</p>
      </footer>
    </div>
  );
}
