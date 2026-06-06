import os
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

DATABASE_URL = os.environ.get('DATABASE_URL')
SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'community.db')

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

CATEGORIES = [
    'Game Dev', 'Game Discussion', 'Showcase',
    'Resources', 'Collaboration', 'Pixel Art', 'Game Jams'
]

def get_db():
    if 'db' not in g:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            g.db = conn
        else:
            import sqlite3
            conn = sqlite3.connect(SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            g.db = conn
    return g.db

def query_db(query, args=(), one=False):
    db = get_db()
    if DATABASE_URL:
        pg_query = query.replace('?', '%s')
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(pg_query, args)
            if query.strip().upper().startswith('SELECT'):
                rows = cur.fetchall()
                return (rows[0] if rows else None) if one else rows
    else:
        import sqlite3
        cur = db.execute(query, args)
        if query.strip().upper().startswith('SELECT'):
            rows = cur.fetchall()
            return (rows[0] if rows else None) if one else rows
        db.commit()
    return None

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    if DATABASE_URL:
        with db.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    avatar TEXT DEFAULT '',
                    bio TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TEXT NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER NOT NULL REFERENCES posts(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
    else:
        import sqlite3
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                avatar TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')
        db.commit()

with app.app_context():
    init_db()

def now():
    return datetime.utcnow().isoformat() + 'Z'

@app.before_request
def load_user():
    g.user = None
    user_id = session.get('user_id')
    if user_id:
        g.user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)

@app.route('/')
def index():
    category = request.args.get('category')
    sort = request.args.get('sort', 'recent')
    search = request.args.get('q', '').strip()

    query = '''
        SELECT p.*, u.username,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
        FROM posts p JOIN users u ON p.user_id = u.id
    '''
    conditions = []
    params = []

    if category:
        conditions.append('p.category = ?')
        params.append(category)
    if search:
        conditions.append('(p.title LIKE ? OR p.content LIKE ?)')
        params.extend([f'%{search}%', f'%{search}%'])

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY p.created_at DESC'

    posts = query_db(query, params)
    top_users = query_db('''
        SELECT u.id, u.username, COUNT(p.id) as post_count
        FROM users u LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id ORDER BY post_count DESC LIMIT 5
    ''')

    return render_template('index.html', posts=posts, categories=CATEGORIES,
                           selected_category=category, search=search,
                           sort=sort, top_users=top_users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.')
            return render_template('register.html')
        try:
            query_db('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                     (username, password, now()))
            user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
            session['user_id'] = user['id']
            flash('Welcome aboard, indie dev!')
            return redirect(url_for('index'))
        except Exception:
            flash('Username already taken.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ? AND password = ?',
                        (username, password), one=True)
        if user:
            session['user_id'] = user['id']
            flash('Welcome back!')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    if not g.user:
        flash('Please login first.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        category = request.form['category']
        if not title or not content:
            flash('Title and content are required.')
            return render_template('new_post.html', categories=CATEGORIES)
        query_db('INSERT INTO posts (title, content, category, user_id, created_at) VALUES (?, ?, ?, ?, ?)',
                 (title, content, category, g.user['id'], now()))
        flash('Post created!')
        return redirect(url_for('index'))
    return render_template('new_post.html', categories=CATEGORIES)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = query_db('''
        SELECT p.*, u.username FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (post_id,), one=True)
    if not post:
        flash('Post not found.')
        return redirect(url_for('index'))

    if request.method == 'POST' and g.user:
        content = request.form['content'].strip()
        if content:
            query_db('INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
                     (post_id, g.user['id'], content, now()))
            flash('Comment added!')
            return redirect(url_for('view_post', post_id=post_id))

    comments = query_db('''
        SELECT c.*, u.username FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ? ORDER BY c.created_at ASC
    ''', (post_id,))

    return render_template('post.html', post=post, comments=comments)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
    if not user:
        flash('User not found.')
        return redirect(url_for('index'))
    posts = query_db('''
        SELECT p.*, (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
        FROM posts p WHERE p.user_id = ? ORDER BY p.created_at DESC
    ''', (user_id,))
    return render_template('profile.html', profile_user=user, posts=posts)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
