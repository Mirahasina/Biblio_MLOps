const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function fetchBooks() {
  const res = await fetch(`${API_BASE}/books/`);
  if (!res.ok) throw new Error("Échec du chargement des livres");
  return res.json();
}

export async function createBook(book) {
  const res = await fetch(`${API_BASE}/books/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(book),
  });
  if (!res.ok) throw new Error("Échec de la création du livre");
  return res.json();
}

export async function updateBook(id, book) {
  const res = await fetch(`${API_BASE}/books/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(book),
  });
  if (!res.ok) throw new Error("Échec de la mise à jour du livre");
  return res.json();
}

export async function deleteBook(id) {
  const res = await fetch(`${API_BASE}/books/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Échec de la suppression du livre");
}
