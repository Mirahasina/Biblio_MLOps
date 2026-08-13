import { useState, useEffect } from "react";
import {
  fetchBooks,
  createBook,
  updateBook,
  deleteBook,
} from "../api/api";

const EMPTY_FORM = {
  title: "",
  author: "",
  isbn: "",
  genre: "general",
  price: "",
  available: true,
};

export default function BookCRUD() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const data = await fetchBooks();
      setBooks(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      price: parseFloat(form.price),
    };

    try {
      if (editingId) {
        await updateBook(editingId, payload);
      } else {
        await createBook(payload);
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      await loadBooks();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (book) => {
    setEditingId(book.id);
    setForm({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      genre: book.genre,
      price: book.price.toString(),
      available: book.available,
    });
  };

  const handleDelete = async (id) => {
    if (!confirm("Supprimer ce livre ?")) return;
    try {
      await deleteBook(id);
      await loadBooks();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
  };

  return (
    <div className="crud-container">
      <h2>Gestion des livres</h2>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="book-form">
        <input
          name="title"
          placeholder="Titre"
          value={form.title}
          onChange={handleChange}
          required
        />
        <input
          name="author"
          placeholder="Auteur"
          value={form.author}
          onChange={handleChange}
          required
        />
        <input
          name="isbn"
          placeholder="ISBN"
          value={form.isbn}
          onChange={handleChange}
        />
        <input
          name="genre"
          placeholder="Genre"
          value={form.genre}
          onChange={handleChange}
        />
        <input
          name="price"
          type="number"
          step="0.01"
          placeholder="Prix (Ar)"
          value={form.price}
          onChange={handleChange}
          required
        />
        <label>
          <input
            name="available"
            type="checkbox"
            checked={form.available}
            onChange={handleChange}
          />
          Disponible
        </label>
        <div className="form-actions">
          <button type="submit">
            {editingId ? "Mettre à jour" : "Ajouter"}
          </button>
          {editingId && (
            <button type="button" onClick={handleCancel}>
              Annuler
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <table className="book-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Titre</th>
              <th>Auteur</th>
              <th>ISBN</th>
              <th>Genre</th>
              <th>Prix</th>
              <th>Disponible</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {books.map((b) => (
              <tr key={b.id}>
                <td>{b.id}</td>
                <td>{b.title}</td>
                <td>{b.author}</td>
                <td>{b.isbn}</td>
                <td>{b.genre}</td>
                <td>{Math.round(b.price).toLocaleString("fr-MG")} Ar</td>
                <td className={b.available ? "status-yes" : "status-no"}>
                  {b.available ? "Oui" : "Non"}
                </td>
                <td>
                  <button className="btn-edit" onClick={() => handleEdit(b)}>
                    Modifier
                  </button>
                  <button className="btn-delete" onClick={() => handleDelete(b.id)}>
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
