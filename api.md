# API Documentation

## Base URL

### Note: Once the app is deployed, we will need to change all instances of "cozycorner.com" to the actual host.

```
http://cozycorner.com
```

## Endpoints

### 1. Home Route

#### `GET /`

**Description:** Serves the home page.

**Request Example:**

```http
GET / HTTP/1.1
Host: cozycorner.com
```

**Response:**

- Renders `home.html`
- If an error occurs (e.g., invalid username), an error message is displayed on the page.

---

#### `POST /`

**Description:** Authenticates a user based on their username.

**Request Example:**

```http
POST / HTTP/1.1
Host: cozycorner.com
Content-Type: application/x-www-form-urlencoded

username=johndoe
```

**Response Behavior:**

- If the username exists in the database:
  - The session stores `user_id` and `username`.
  - Redirects to `/userBookShelf`.
- If the username is invalid:
  - Returns `home.html` with an error message: `"Invalid username. Please try again."`

**Request Body Parameters:**

| Parameter  | Type   | Required | Description                  |
| ---------- | ------ | -------- | ---------------------------- |
| `username` | string | Yes      | The username to authenticate |

**Possible Responses:**

| Status Code | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| 200 OK      | Renders `home.html` (GET request or failed authentication)   |
| 302 Found   | Redirects to `/userBookShelf` upon successful authentication |

---

### 2. Create Account Route

#### `GET /create_account`

**Description:** Serves the account creation page.

**Request Example:**

```http
GET /create_account HTTP/1.1
Host: cozycorner.com
```

**Response:**

- Renders `create_account.html`
- If an error occurs (e.g., duplicate username), an error message is displayed on the page.

---

#### `POST /create_account`

**Description:** Creates a new user account.

**Request Example:**

```http
POST /create_account HTTP/1.1
Host: cozycorner.com
Content-Type: application/x-www-form-urlencoded

username=newuser
```

**Response Behavior:**

- If the username is unique:
  - Inserts the username into the database.
  - Redirects to `/` (home page).
- If the username already exists:
  - Returns `create_account.html` with an error message: `"Username already exists. Try another one."`

**Request Body Parameters:**

| Parameter  | Type   | Required | Description                           |
| ---------- | ------ | -------- | ------------------------------------- |
| `username` | string | Yes      | The username to create a new account |

**Possible Responses:**

| Status Code | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| 200 OK      | Renders `create_account.html` (GET request or duplicate username) |
| 302 Found   | Redirects to `/` upon successful account creation |

---

### 3. User Bookshelf Route

#### `GET /userBookShelf`

**Description:** Displays the user's bookshelf.

**Request Example:**

```http
GET /userBookShelf HTTP/1.1
Host: cozycorner.com
```

**Response Behavior:**

- If the user is authenticated:
  - Retrieves books from the database for the logged-in user.
  - Displays books categorized into shelves.
  - Renders `userBookShelf.html` with the user's books.
- If the user is not authenticated:
  - Redirects to `/` (home page).

**Possible Responses:**

| Status Code | Description                                      |
| ----------- | ------------------------------------------------ |
| 200 OK      | Renders `userBookShelf.html` with user's books.  |
| 302 Found   | Redirects to `/` if the user is not authenticated. |

---

### 4. Add Book Route

#### `GET /add_book`

**Description:** Serves the page for adding a new book.

**Request Example:**

```http
GET /add_book HTTP/1.1
Host: cozycorner.com
```

**Response:**

- Renders `add_book.html`

---

#### `POST /add_book`

**Description:** Adds a new book to the user's bookshelf.

**Request Example:**

```http
POST /add_book HTTP/1.1
Host: cozycorner.com
Content-Type: application/x-www-form-urlencoded

title=BookTitle&author=AuthorName&genre=Fiction&cover_image=/static/assets/image/cover.jpg&has_read=1&in_collection=1
```

**Request Body Parameters:**

| Parameter      | Type   | Required | Description                                       |
| ------------- | ------ | -------- | ------------------------------------------------- |
| `title`       | string | Yes      | The title of the book                            |
| `author`      | string | Yes      | The author of the book                           |
| `genre`       | string | Yes      | The genre of the book                            |
| `cover_image` | string | No       | The URL of the book cover image (optional)       |
| `has_read`    | int    | No       | `1` if the book has been read, otherwise `0`     |
| `in_collection` | int    | No       | `1` if the book is in the collection, otherwise `0` |

**Response Behavior:**

- Adds the book to the `BOOK` table.
- Links the book to the user in the `BOOKSHELF` table.
- Redirects to `/userBookShelf`.

**Possible Responses:**

| Status Code | Description                                      |
| ----------- | ------------------------------------------------ |
| 200 OK      | Renders `add_book.html` (GET request)            |
| 302 Found   | Redirects to `/userBookShelf` after book addition |

---

### 8. Logout Route

#### `GET /logout`

**Description:** Logs out the current user.

**Request Example:**

```http
GET /logout HTTP/1.1
Host: cozycorner.com
```

**Response Behavior:**

- Removes `user_id` and `username` from the session.
- Redirects to `/` (home page).

**Possible Responses:**

| Status Code | Description                                      |
| ----------- | ------------------------------------------------ |
| 302 Found   | Redirects to `/` after logout |



## Notes

- The database connection uses `sqlite3`.
- Sessions store authenticated user details (`user_id`, `username`).





