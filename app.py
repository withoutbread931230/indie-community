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
    'General Guides', 'Tips & Tricks', 'Walkthroughs',
    'Mods & Modding', 'Cities: Skylines 2', 'Showcase', 'Discussion'
]

CATEGORY_ICONS = {
    'General Guides': '📖',
    'Tips & Tricks': '💡',
    'Walkthroughs': '🗺️',
    'Mods & Modding': '🔧',
    'Cities: Skylines 2': '🏙️',
    'Showcase': '🎮',
    'Discussion': '💬',
}

GAMES = [
    {'name': 'Cities: Skylines 2', 'icon': '🏙️', 'color': '#4a90d9', 'slug': 'cities-skylines-2'},
    {'name': 'Baldur\'s Gate 3', 'icon': '⚔️', 'color': '#c43a31', 'slug': 'baldurs-gate-3'},
    {'name': 'Elden Ring', 'icon': '🗡️', 'color': '#8b7355', 'slug': 'elden-ring'},
    {'name': 'Stardew Valley', 'icon': '🌾', 'color': '#5b8c5a', 'slug': 'stardew-valley'},
    {'name': 'Cyberpunk 2077', 'icon': '🔷', 'color': '#ff6b35', 'slug': 'cyberpunk-2077'},
    {'name': 'Hollow Knight', 'icon': '🐞', 'color': '#5a4a7a', 'slug': 'hollow-knight'},
]

SEED_POSTS = [
    {
        'title': 'Cities: Skylines 2 — Beginner\'s Guide to Building Your First City',
        'content': (
            'Starting your first city in Cities: Skylines 2 can be overwhelming. Here\'s a step-by-step guide to get you started on the right foot.\n\n'
            '## 1. Choose Your Map Wisely\n'
            'Start with a temperate map like \"Windy Fjords\" or \"Great Highlands\". These have balanced resources and forgiving terrain. Avoid maps with extreme mountains or limited water access for your first playthrough.\n\n'
            '## 2. Road Hierarchy is Everything\n'
            'The single most important concept in CS2 is road hierarchy. Always plan your roads in layers:\n'
            '- Highways (6 lanes) for long-distance connections\n'
            '- Arterial roads (4 lanes) connecting districts\n'
            '- Collector roads (2 lanes) distributing local traffic\n'
            '- Local roads for residential zones\n\n'
            '## 3. Zone Smart, Not Fast\n'
            'Don\'t zone everything at once. Start with a small residential block, add basic services (water, power, sewage), and let the city grow organically. Watch your demand bars — they tell you exactly what your city needs.\n\n'
            '## 4. Manage Budget Early\n'
            'Lower your service budgets to 50% at the start. You don\'t need full funding for schools and hospitals when your population is under 500. Increase gradually as your city grows.\n\n'
            '## 5. Embrace Public Transit Early\n'
            'Even a small bus route connecting residential to industrial zones will dramatically reduce traffic. Upgrade to trams and metro as your city expands.\n\n'
            'Remember: every great city started with a single road. Take your time and enjoy the process!'
        ),
        'category': 'Cities: Skylines 2',
        'username': 'CityPlanner',
        'cover_url': 'https://picsum.photos/seed/cs2-beginner/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Top 15 Must-Have Mods for Cities: Skylines 2 (2026)',
        'content': (
            'The CS2 modding scene has exploded. Here are the mods you absolutely need:\n\n'
            '## Essential Gameplay Mods\n'
            '**1. Traffic Manager** — The gold standard for traffic control. Custom lane arrows, speed limits, and timed traffic lights give you pixel-perfect control over your road network.\n\n'
            '**2. Move It!** — Fine-tune every building, road, and prop. Perfect for fixing those awkward zoning alignments.\n\n'
            '**3. Fine Road Anarchy** — Place roads anywhere, at any angle. No more snapping frustrations.\n\n'
            '## Visual Enhancement Mods\n'
            '**4. Render It!** — Lumen-based global illumination for jaw-dropping visuals. A must for screenshot enthusiasts.\n\n'
            '**5. Ultimate Level of Detail (ULOD)** — Push LOD distances beyond vanilla limits for crisp visuals.\n\n'
            '## Quality of Life Mods\n'
            '**6. 81 Tiles 2** — Unlock the entire map for building.\n'
            '**7. Demand Master** — Fine-tune RCI demand to your liking.\n'
            '**8. Better Bulldozer** — Delete multiple items at once with custom brush sizes.\n\n'
            '## Performance Mods\n'
            '**9. FPS Booster** — Disables unnecessary rendering for smoother gameplay.\n'
            '**10. Render Limits Toggle** — Adjust simulation and rendering distances based on your hardware.\n\n'
            'All mods are available on Paradox Mods and Thunderstore. Always check compatibility before installing!'
        ),
        'category': 'Mods & Modding',
        'username': 'ModMaster',
        'cover_url': 'https://picsum.photos/seed/cs2-mods/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Traffic Engineering 101 — Solving Gridlock in Cities: Skylines 2',
        'content': (
            'Traffic is the #1 challenge in CS2. Here\'s how to fix it like a pro.\n\n'
            '## The Root Cause\n'
            'Most traffic jams happen at intersections. Every time a car stops at an intersection, it creates a ripple effect. The solution? Minimize intersections and optimize those you can\'t remove.\n\n'
            '## Roundabouts: Your Best Friend\n'
            'A well-designed roundabout handles 3x more traffic than a signaled intersection. Key rules:\n'
            '- Keep them small (3-4 cells radius)\n'
            '- Never place intersections too close to the roundabout\n'
            '- Use highway ramps for high-traffic connections\n\n'
            '## Road Hierarchy in Practice\n'
            'Your city needs clear traffic arteries. Think of it like the human body:\n'
            '- Highways = arteries (high speed, high volume)\n'
            '- Arterial roads = veins (connect neighborhoods)\n'
            '- Local roads = capillaries (slow, local only)\n\n'
            '## Public Transit is Not Optional\n'
            'A single metro line can remove 500+ cars from your roads. Always build transit BEFORE traffic gets bad — it\'s much harder to retrofit.\n\n'
            '## Mods That Help\n'
            'Traffic Manager (TM) lets you customize lane arrows, create timed traffic lights, and set speed limits per road segment. Game-changing.'
        ),
        'category': 'Cities: Skylines 2',
        'username': 'TrafficGuru',
        'cover_url': 'https://picsum.photos/seed/cs2-traffic/800/400',
        'days_ago': 5,
    },
    {
        'title': 'Stardew Valley — Complete Year 1 Guide (Spring)',
        'content': (
            'Maximize your first spring in Stardew Valley with this day-by-day guide.\n\n'
            '## Day 1-5: The Grind\n'
            '- Clear exactly 50-100 tiles of your farm for planting\n'
            '- Visit Pierre\'s to buy parsnip seeds (15-20 is plenty)\n'
            '- Explore the town and meet everyone (gifts matter!)\n'
            '- Fish at the mountain lake for easy money\n\n'
            '## Day 6-12: First Profits\n'
            '- Your parsnips should be ready by day 6-7\n'
            '- Save 2,000g for strawberry seeds at the Egg Festival (day 13)\n'
            '- Upgrade your backpack at Pierre\'s ASAP\n'
            '- Start mining in the mountain cave for copper ore\n\n'
            '## Day 13-20: Egg Festival & Expansion\n'
            '- BUY STRAWBERRIES. Plant them the same day.\n'
            '- With speed-gro fertilizer, you get 2 harvests before summer\n'
            '- Continue mining to reach floor 40+ for iron ore\n\n'
            '## Day 21-28: Pre-Summer Prep\n'
            '- Save at least 5,000g for summer seeds\n'
            '- Build a silo if you have animals (4000g, 100 stone, 10 clay, 5 copper)\n'
            '- Stockpile wood and stone — you\'ll need them\n\n'
            'Pro tip: check the TV every day for luck forecasts and recipes!'
        ),
        'category': 'Walkthroughs',
        'username': 'FarmHand',
        'cover_url': 'https://picsum.photos/seed/stardew/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Elden Ring — 10 Tips That Make the Game Actually Fun',
        'content': (
            'Elden Ring doesn\'t hold your hand. Here\'s what I wish I knew before starting.\n\n'
            '## 1. Vigor is Non-Negotiable\n'
            'Level VIGOR to at least 30 before touching any other stat much. More HP means more mistakes you can learn from.\n\n'
            '## 2. Explore Limgrave Thoroughly\n'
            'The starting area is packed with upgrade materials, flask upgrades, and useful talismans. Don\'t rush to Stormveil Castle — explore every cave and ruin first.\n\n'
            '## 3. Use Ashes of War\n'
            'They\'re not just weapon arts — they let you change your weapon\'s scaling and damage type. A \"Heavy\" affinity turns a DEX weapon into a STR weapon.\n\n'
            '## 4. Level Your Weapon, Not Just Your Character\n'
            'Weapon upgrades matter more than stat points early on. Explore mines (marked with orange circles on the map) for smithing stones.\n\n'
            '## 5. Spirit Ashes Are Your Friend\n'
            'The Lone Wolf Ashes you get early can carry you through tough bosses. Don\'t be proud — use them.\n\n'
            '## 6. Read Item Descriptions\n'
            'Almost every piece of lore and many gameplay hints are hidden in item descriptions. Your map even has guidance!\n\n'
            '## 7. Don\'t Kill NPCs\n'
            'Really. Just don\'t. You\'ll lock yourself out of quests and gear.\n\n'
            '## 8. Use Guard Counters\n'
            'Block an attack and immediately heavy attack for a powerful counter. This breaks enemy stance quickly.\n\n'
            '## 9. Torrent Can Double Jump\n'
            'Yes, your spectral steed can double jump. This makes exploring much easier.\n\n'
            '## 10. Death is Progress\n'
            'You will die. A lot. Every death teaches you something. Embrace it.'
        ),
        'category': 'Tips & Tricks',
        'username': 'TarnishedOne',
        'cover_url': 'https://picsum.photos/seed/eldenring/800/400',
        'days_ago': 6,
    },
    {
        'title': 'Baldur\'s Gate 3 — Top 5 Most Powerful Class Builds',
        'content': (
            'Whether you\'re a veteran or a newcomer, these builds will carry you through Tactician mode.\n\n'
            '## 1. Sorlock (Sorcerer 10 / Warlock 2)\n'
            'The quintessential blaster. Quickened Eldritch Blast with Agonizing Blast deals insane damage. Combine with Haste for 6-9 beams per turn. Race: Half-Elf for bonus movement.\n\n'
            '## 2. Open Hand Monk 9 / Thief 3\n'
            'With 3 bonus actions per turn (Thief\'s Fast Hands + Monk\'s Wholeness of Body), you\'re a blender. Tavern Brawler feat + STR elixirs = each punch hits for 20+ damage.\n\n'
            '## 3. Battle Master 12\n'
            'Simple but devastating. Great Weapon Master + Sentinel + Polearm Master. Trip Attack into Action Surge is a delete button. Race: Wood Half-Elf for movement.\n\n'
            '## 4. Light Cleric 12\n'
            'Best support in the game. Warding Flare protects allies, Spirit Guardians melts groups, and Radiance of the Dawn is an AoE nuke. Gear for CON saves to maintain concentration.\n\n'
            '## 5. Gloom Stalker 5 / Assassin 3 / Battle Master 4\n'
            'The first-round killer. 6+ attacks on turn 1 with insane initiative. Guaranteed crits on surprised enemies. Perfect for initiating every fight.\n\n'
            'All builds work on Balanced and Tactician. Honour Mode requires extra caution regardless of build!'
        ),
        'category': 'Walkthroughs',
        'username': 'DungeonDelver',
        'cover_url': 'https://picsum.photos/seed/bg3/800/400',
        'days_ago': 7,
    },
    {
        'title': 'Cyberpunk 2077 2.2 — Best Cyberware Loadout for Each Playstyle',
        'content': (
            'With the 2.2 update, cyberware choices matter more than ever. Here\'s what to equip for each build.\n\n'
            '## Sandevistan Build (Slow-Mo Melee)\n'
            '- **Axolotl** (Frontal Cortex): Resets Sandevistan cooldown on kills\n'
            '- **Apogee Sandevistan** (Nervous System): Best in slot, 85% slow\n'
            '- **Microrotors** (Hands): +30% attack speed\n'
            '- **Lynx Paws** (Legs): Silent movement for stealth approach\n\n'
            '## Netrunner Build (Quickhacks Only)\n'
            '- **Tetratronic Rippler** (Operating System): Hacks spread between enemies\n'
            '- **Bioconductors** (Frontal Cortex): +4 RAM capacity\n'
            '- **Synaptic Accelerator** (Nervous System): Slow time when detected\n'
            '- **Smart Link** (Hands): Smart weapon synergy\n\n'
            '## Berserk Build (Shotgun/Melee Tank)\n'
            '- **Berserk** (Operating System): Health regen + damage reduction\n'
            '- **Universal Booster** (Frontal Cortex): Health item efficiency\n'
            '- **Microgenerator** (Hands): Electric damage on reload\n'
            '- **Fortified Ankles** (Legs): Superhero landing\n\n'
            'Remember to visit Ripperdocs in Dogtown for the best iconic chrome!'
        ),
        'category': 'General Guides',
        'username': 'NetRunnerX',
        'cover_url': 'https://picsum.photos/seed/cyberpunk/800/400',
        'days_ago': 8,
    },
    {
        'title': 'Hollow Knight — Hidden Secrets You Probably Missed',
        'content': (
            'Hallownest is full of secrets. Here are the ones most players never find.\n\n'
            '## The Abyss Creature\n'
            'After getting Void Heart, return to the Abyss and swim to the bottom-left area. You\'ll find a hidden room with a giant creature. Hitting it reveals a secret dialogue with the Hunter.\n\n'
            '## The Jinn Collector\n'
            'In the Kingdom\'s Edge, there\'s a hidden room with a ghostly bug called Jinn. She buys your rancid eggs for 1,000 geo each — way better than the regular 250.\n\n'
            '## Path of Pain\n'
            'In the White Palace, there\'s a hidden breakable wall near the top of the tower. Breaking it leads to the Path of Pain — the hardest platforming challenge in the game. The reward? A lore cutscene and bragging rights.\n\n'
            '## Mr. Mushroom\n'
            'Dream nail the mushroom enemies in Fungal Wastes repeatedly. Each time you do, Mr. Mushroom appears. Follow him through multiple rooms for a secret ending.\n\n'
            '## The Eternal Ordeal\n'
            'In the Godhome DLC, hit the ghost in the top-left corner of the main hub. This unlocks the Eternal Ordeal — an endless wave of Zotelings. Survive 57 waves for a unique journal entry.\n\n'
            '## Grey Prince Zote\n'
            'If you saved Zote (why would you?), he appears as a boss in Godhome. Each time you beat him, he gets stronger. There are 10 tiers. Good luck.'
        ),
        'category': 'Tips & Tricks',
        'username': 'BugHunter',
        'cover_url': 'https://picsum.photos/seed/hollowknight/800/400',
        'days_ago': 10,
    },
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
                    created_at TEXT NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    cover_url TEXT DEFAULT '',
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
            try:
                cur.execute('ALTER TABLE posts ADD COLUMN IF NOT EXISTS cover_url TEXT DEFAULT \'\'')
            except Exception:
                pass
    else:
        import sqlite3
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                cover_url TEXT DEFAULT '',
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
        try:
            db.execute('ALTER TABLE posts ADD COLUMN cover_url TEXT DEFAULT \'\'')
            db.commit()
        except Exception:
            pass

def seed_data():
    existing = query_db('SELECT COUNT(*) as cnt FROM posts')
    if existing and existing['cnt'] > 0:
        return
    from datetime import timedelta
    base_time = datetime.utcnow()
    for i, post in enumerate(SEED_POSTS):
        user = query_db('SELECT id FROM users WHERE username = ?', (post['username'],), one=True)
        if not user:
            query_db('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                     (post['username'], 'guide123', (base_time - timedelta(days=post['days_ago'] + 1)).isoformat() + 'Z'))
            user = query_db('SELECT id FROM users WHERE username = ?', (post['username'],), one=True)
        created = (base_time - timedelta(days=post['days_ago'])).isoformat() + 'Z'
        query_db(
            'INSERT INTO posts (title, content, category, cover_url, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (post['title'], post['content'], post['category'], post['cover_url'], user['id'], created)
        )

with app.app_context():
    init_db()
    seed_data()

def now():
    return datetime.utcnow().isoformat() + 'Z'

def get_category_icon(category):
    return CATEGORY_ICONS.get(category, '📋')

@app.before_request
def load_user():
    g.user = None
    user_id = session.get('user_id')
    if user_id:
        g.user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)

@app.route('/')
def index():
    category = request.args.get('category')
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

    cs2_posts = [p for p in posts if p['category'] == 'Cities: Skylines 2'][:3] if posts else []

    return render_template('index.html', posts=posts, categories=CATEGORIES,
                           get_category_icon=get_category_icon,
                           selected_category=category, search=search,
                           top_users=top_users, games=GAMES, cs2_posts=cs2_posts)

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
            flash('Welcome aboard, gamer!')
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
        cover_url = request.form.get('cover_url', '').strip()
        if not title or not content:
            flash('Title and content are required.')
            return render_template('new_post.html', categories=CATEGORIES, get_category_icon=get_category_icon)
        query_db('INSERT INTO posts (title, content, category, cover_url, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                 (title, content, category, cover_url, g.user['id'], now()))
        flash('Guide published!')
        return redirect(url_for('index'))
    return render_template('new_post.html', categories=CATEGORIES, get_category_icon=get_category_icon)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = query_db('''
        SELECT p.*, u.username FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    ''', (post_id,), one=True)
    if not post:
        flash('Guide not found.')
        return redirect(url_for('index'))

    if request.method == 'POST' and g.user:
        content = request.form['content'].strip()
        if content:
            query_db('INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
                     (post_id, g.user['id'], content, now()))
            flash('Comment posted!')
            return redirect(url_for('view_post', post_id=post_id))

    comments = query_db('''
        SELECT c.*, u.username FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ? ORDER BY c.created_at ASC
    ''', (post_id,))

    return render_template('post.html', post=post, comments=comments,
                           get_category_icon=get_category_icon)

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
    return render_template('profile.html', profile_user=user, posts=posts,
                           get_category_icon=get_category_icon)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
