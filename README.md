# <h1 align="center">📚 CozyCorner 📚</h1>

---

## <h2 align="center"> Description </h2>

**Your Personal Book Collection, Simplified**

Stay on top of your reading progress with our **intuitive app**.  
Add books to your collection, categorize them by reading status, and view essential **details** like titles, authors,
and reading status.  
Easily **search** for specific books, and update your collection to reflect **new reads** or books you no longer own.

---

## <h2 align="center"> Setup Instructions </h2>

1. **Clone Repository from GitHub**

```
git clone https://github.com/LoganPickell/AgileArchitects_ModernSoftwareDevelopment.git
```

2. **Create a virtual environment** (optional but recommended):

```
python -m venv venv
```

3. **Activate the virtual environment**:
    - **Windows**:
      ```
      .\venv\Scripts\activate
      ```
    - **Mac/Linux**:
      ```
      source venv/bin/activate
      ```

4. **Install dependencies using** `requirements.txt`:

```
pip install -r requirements.txt
```

5. **Run the app**:

```
python app.py
```

---

## <h2 align="center"> How to Use the App </h2>

#### 1. Create your account! 💻
1. Click "Create Account" and create a username
2. Login with your username

#### 2. Find books! 📖
* Go to "Add New Book" to manually add a book to your bookshelf
* Go to "Search Books" to find any book by its title or author

    * Ex. Search "Stephen King" to find all of his books
    * Ex. Search "Twilight" to find the specific book itself
* If you have read the book before, check "Have you read this book?"
* If you own the book, check "Do you own this book?"
#### 3. Look at what's in your bookshelf! 👀
* You may edit book details by clicking the pencil icon ✏️
* You may delete books from your bookshelf by clicking the trash icon 🗑️
* You may favorite books from your bookshelf by clicking the heart icon ❤️
#### 4. Ensure you logout! 😁
* Simply go to your bookshelf and press "Logout" next to the welcome message

---

## <h2 align="center"> Screenshots </h2>

![home login page](screenshots/Home.jpeg)
![create account page](screenshots/CreateAccount.jpeg)
![bookshelf page](screenshots/myBookShelf.jpeg)
![add book page](screenshots/addBook.jpeg)
![edit book page](screenshots/Editbook.jpeg)
![search book page](screenshots/searchbook.jpeg)





# GitHub CD Pipeline with AWS EC2 and Docker

## 1. Launch & Access AWS EC2 Instance

### a. Launch an EC2 Instance
- Launch an EC2 instance using **Ubuntu 22.04 LTS**.
- Configure the **security group** to allow:
  - SSH (Port 22)
  - HTTP (Port 80)
  - Application ports (e.g., 8000)

### b. SSH into the Instance
```bash
chmod 400 cozycorner.pem
ssh -i "cozycorner.pem" ubuntu@3.129.45.79
```
## 2. Install Docker on EC2
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

## 3. Clone Repo to Server
git clone <link to repo> <where you want it>

``` bash
git clone https://github.com/LoganPickell/AgileArchitects_ModernSoftwareDevelopment.git /tmp/deploy-repo
```
## 4. Build Docker Image
Change directory into app folder, then build the image (MUST HAVE 
DOCKERFILE TO BUILD!)

https://github.com/LoganPickell/ AgileArchitects_ModernSoftwareDevelopment/blob/main/Dockerfile

```bash
cd /tmp/deploy-repo
sudo docker build -t cozycorner .
```
in this case our IMAGE name is cozycorner, you will need that name to run 
the container

## 5. Run Docker Image
```bash
sudo docker run -d --name myapp-container -p 80:5000 cozycorner
```
-d runs in detached mode, we specified we want it to be named myapp-
container, port mapping 80:5000 and we want to build the cozycorner 
image.

# Automate Deployment
## 1. Github Actions Workflow
Create .github/workflows/.yml file
https://github.com/LoganPickell/AgileArchitects_ModernSoftwareDevelopment/blob/main/.github/workflows/ci.yml

## 2. Add Secrets to GitHub
In GitHub repo settings → Secrets and variables → Actions:
- Add `SERVER_SSH_KEY` and paste the contents of your `.pem` file
- Add `SERVER_USER` and paste the user name – in our case it is ‘ubuntu’
- Add ‘SERVER_IP’ and paste the IP address to the server in. (3.129.45.79)




