#!/usr/bin/env python3
"""Seed massif de livres via l'API CRUD."""

import json
import random
import urllib.request

API = "http://localhost:8000/api/books/"

TITLES = [
    "Les Misérables", "Le Petit Prince", "1984", "L'Étranger", "Madame Bovary",
    "Crime et Châtiment", "Guerre et Paix", "Don Quichotte", "Hamlet", "Othello",
    "Orgueil et Préjugés", "Jane Eyre", "Wuthering Heights", "Moby Dick", "Dracula",
    "Frankenstein", "Le Comte de Monte-Cristo", "Les Fleurs du Mal", "Candide",
    "Germinal", "Nana", "Bel-Ami", "La Peste", "L'Homme révolté", "Siddhartha",
    "Le Nom de la Rose", "Harry Potter", "Le Seigneur des Anneaux", "Dune",
    "Fondation", "Neuromancien", "Fahrenheit 451", "Brave New World", "Animal Farm",
    "To Kill a Mockingbird", "The Great Gatsby", "Catch-22", "Lolita", "Ulysses",
    "One Hundred Years of Solitude", "Beloved", "The Handmaid's Tale", "Sapiens",
    "Homo Deus", "Atomic Habits", "Deep Work", "Clean Code", "Design Patterns",
    "The Pragmatic Programmer", "Introduction to Algorithms", "Python Crash Course",
    "Fluent Python", "Kubernetes in Action", "Site Reliability Engineering",
    "The Phoenix Project", "Accelerate", "Continuous Delivery", "Domain-Driven Design",
    "Refactoring", "Effective Java", "You Don't Know JS", "Eloquent JavaScript",
    "Learning React", "Full Stack FastAPI", "PostgreSQL Internals", "Airflow Guide",
    "MLOps Engineering", "Data Pipelines", "The Data Warehouse Toolkit",
    "Streaming Systems", "Designing Data-Intensive Applications", "System Design",
    "Zero to One", "The Lean Startup", "Thinking Fast and Slow", "Outliers",
    "The Alchemist", "Life of Pi", "The Kite Runner", "A Thousand Splendid Suns",
    "Norwegian Wood", "Kafka on the Shore", "1Q84", "Snow Country", "Kokoro",
    "Things Fall Apart", "Half of a Yellow Sun", "Americanah", "Purple Hibiscus",
    "The God of Small Things", "Midnight's Children", "A Suitable Boy",
    "The Remains of the Day", "Never Let Me Go", "Klara and the Sun",
    "Cloud Atlas", "The Road", "Blood Meridian", "No Country for Old Men",
    "The Martian", "Project Hail Mary", "Ready Player One", "Snow Crash",
]

AUTHORS = [
    "Victor Hugo", "Antoine de Saint-Exupéry", "George Orwell", "Albert Camus",
    "Gustave Flaubert", "Fyodor Dostoevsky", "Leo Tolstoy", "Miguel de Cervantes",
    "William Shakespeare", "Jane Austen", "Charlotte Brontë", "Emily Brontë",
    "Herman Melville", "Bram Stoker", "Mary Shelley", "Alexandre Dumas",
    "Charles Baudelaire", "Voltaire", "Émile Zola", "Guy de Maupassant",
    "Hermann Hesse", "Umberto Eco", "J.K. Rowling", "J.R.R. Tolkien",
    "Frank Herbert", "Isaac Asimov", "William Gibson", "Ray Bradbury",
    "Aldous Huxley", "Harper Lee", "F. Scott Fitzgerald", "Joseph Heller",
    "Vladimir Nabokov", "James Joyce", "Gabriel García Márquez", "Toni Morrison",
    "Margaret Atwood", "Yuval Noah Harari", "James Clear", "Cal Newport",
    "Robert C. Martin", "Gang of Four", "Andy Hunt", "Thomas Cormen",
    "Eric Matthes", "Luciano Ramalho", "Marko Lukša", "Google SRE",
    "Gene Kim", "Nicole Forsgren", "Jez Humble", "Eric Evans",
    "Martin Fowler", "Joshua Bloch", "Kyle Simpson", "Marijn Haverbeke",
    "Alex Banks", "Sebastian Ramirez", "Bruce Momjian", "Apache Airflow",
    "Noah Gift", "Joe Reis", "Ralph Kimball", "Tyler Akidau",
    "Martin Kleppmann", "Alex Xu", "Peter Thiel", "Eric Ries",
    "Daniel Kahneman", "Malcolm Gladwell", "Paulo Coelho", "Yann Martel",
    "Khaled Hosseini", "Haruki Murakami", "Yasunari Kawabata", "Natsume Sōseki",
    "Chinua Achebe", "Chimamanda Ngozi Adichie", "Arundhati Roy", "Salman Rushdie",
    "Vikram Seth", "Kazuo Ishiguro", "David Mitchell", "Cormac McCarthy",
    "Andy Weir", "Ernest Cline", "Neal Stephenson",
]

GENRES = [
    "roman", "science-fiction", "fantasy", "classique", "philosophie",
    "technologie", "devops", "data", "biographie", "thriller",
    "histoire", "poésie", "essai", "jeunesse", "business",
]

# Variantes pour multiplier les entrées
SUFFIXES = ["", " - Tome 1", " - Tome 2", " - Édition collector", " - Annoté", " - Résumé"]


def make_books(count: int = 250) -> list[dict]:
    books = []
    for i in range(count):
        title = random.choice(TITLES) + random.choice(SUFFIXES)
        if i >= len(TITLES):
            title = f"{title} #{i + 1}"
        books.append(
            {
                "title": title,
                "author": random.choice(AUTHORS),
                "isbn": f"978-{random.randint(0,9)}-{random.randint(100000,999999)}-{random.randint(100,999)}-{random.randint(0,9)}",
                "genre": random.choice(GENRES),
                "price": round(random.uniform(0, 85) if random.random() > 0.08 else 0.0, 2),
                "available": random.random() > 0.15,  # ~15% indisponibles (pour le filtre ETL)
            }
        )
    return books


def post_book(book: dict) -> bool:
    data = json.dumps(book).encode()
    req = urllib.request.Request(
        API,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception as exc:
        print(f"ERR: {exc} -> {book['title']}")
        return False


def main():
    books = make_books(250)
    ok = 0
    for i, book in enumerate(books, 1):
        if post_book(book):
            ok += 1
        if i % 50 == 0:
            print(f"... {i}/{len(books)} envoyés")
    print(f"OK: {ok}/{len(books)} livres créés")


if __name__ == "__main__":
    main()
