# Planning Document for Agile Architects Book Tracker App

```mermaid
erDiagram

users{
    user_id int PK
    username string
}

BOOK {
    book_id int PK
    title string
    author string
    genre string
    image blob
    
}


BOOKSHELF {
    bookId int  PK
    user_id int PK
    hasRead bool
    inCollection bool
}


BOOKSHELF ||--|| USER : has
BOOKSHELF ||--|{ BOOK : has


```
---
```mermaid
flowchart TD
A[Homepage] --> B[Search Books]
A --> C[Add Book]
A --> E[My Bookshelf]
B --> F[Search Results] --> G[View Book Details]
C --> A
E --> D[Select Book] --> G
G --> H[Edit Book]
G --> I[Delete Book]
G --> J[Mark as Favorite]
G --> K[Update Reading Status]
G --> L[Hide Book]
H --> A
I --> A
J --> M[My Favorites]
K --> A
L --> N[Hidden Books]
M --> G
```
