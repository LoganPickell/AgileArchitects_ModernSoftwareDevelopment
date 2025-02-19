# Planning Document for Agile Architects Book Tracker App

```mermaid
---
title: Book App ER Diagram
---
erdiagram

Entity "User" {
    +user_id: UUID
    ---
    username: string
    email: string
    password: string
}

Entity "Book" {
    +book_id: UUID
    ---
    title: string
    author: string
    genre: string
    publication_year: int
}


Entity "UserBook" {
    +id: UUID
    ---
    status: string
    start_date: date
    end_date: date
}

User ||--o{ UserBook : "Tracks"
Book ||--o{ UserBook : "Tracks"




```