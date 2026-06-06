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
    'Getting Started', 'City Planning', 'Traffic & Transit',
    'Mods & Modding', 'Tips & Tricks', 'Guides & Walkthroughs', 'Showcase'
]

CATEGORY_ICONS = {
    'Getting Started': '🚀',
    'City Planning': '🏗️',
    'Traffic & Transit': '🚇',
    'Mods & Modding': '🔧',
    'Tips & Tricks': '💡',
    'Guides & Walkthroughs': '📖',
    'Showcase': '🏙️',
}

SEED_POSTS = [
    {
        'title': 'Cities: Skylines 2 Beginner\'s Guide — Build Your First City',
        'content': (
            'Starting your first city in Cities: Skylines 2 can be overwhelming. Here\'s a complete step-by-step guide.\n\n'
            '## 1. Choose Your Map Wisely\n'
            'Start with a temperate map like "Windy Fjords" or "Great Highlands". These have balanced resources and forgiving terrain. Avoid maps with extreme mountains or limited water access.\n\n'
            '## 2. Road Hierarchy is Everything\n'
            'The single most important concept in CS2 is road hierarchy. Plan your roads in layers:\n'
            '- **Highways** (6 lanes) for long-distance connections\n'
            '- **Arterial roads** (4 lanes) connecting districts\n'
            '- **Collector roads** (2 lanes) distributing local traffic\n'
            '- **Local roads** for residential zones\n\n'
            '## 3. Zone Smart, Not Fast\n'
            'Start with a small residential block, add basic services (water, power, sewage), and let the city grow organically. Watch your demand bars.\n\n'
            '## 4. Manage Your Budget\n'
            'Lower service budgets to 50% at the start. Increase gradually as your city grows. Don\'t overbuild services.\n\n'
            '## 5. Public Transit Early\n'
            'Even a single bus route connecting residential to industrial zones dramatically reduces traffic. Add trams and metro as you expand.\n\n'
            'Remember: every great city started with a single road. Take your time and enjoy the process!'
        ),
        'category': 'Getting Started',
        'username': 'CityPlanner',
        'cover_url': 'https://picsum.photos/seed/cs2-guide1/800/400',
        'days_ago': 1,
    },
    {
        'title': 'Advanced Road Hierarchy — Traffic Management Masterclass',
        'content': (
            'Traffic is the #1 challenge in CS2. Master these techniques to keep your city flowing.\n\n'
            '## The Root Cause\n'
            'Most traffic jams happen at intersections. Every stop creates a ripple effect. Minimize intersections.\n\n'
            '## Roundabouts: Your Best Friend\n'
            'A well-designed roundabout handles 3x more traffic than a signaled intersection:\n'
            '- Keep them small (3-4 cells radius)\n'
            '- Never place intersections too close to a roundabout\n'
            '- Use highway ramps for high-traffic connections\n\n'
            '## Diverging Diamond Interchanges\n'
            'For highway-to-highway connections, DDIs are the most efficient. They eliminate left-turn conflicts entirely.\n\n'
            '## One-Way Pair Systems\n'
            'For dense downtown areas, pair two one-way streets running opposite directions. This doubles throughput vs two-way streets.\n\n'
            '## Road Hierarchy in Practice\n'
            'Think of it like the human body:\n'
            '- Highways = arteries (high speed, high volume)\n'
            '- Arterial roads = veins (connect neighborhoods)\n'
            '- Local roads = capillaries (slow, local only)\n\n'
            '## Mods That Help\n'
            'Traffic Manager lets you customize lane arrows, create timed traffic lights, and set speed limits per road segment.'
        ),
        'category': 'Traffic & Transit',
        'username': 'TrafficGuru',
        'cover_url': 'https://picsum.photos/seed/cs2-traffic/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Complete Public Transit Guide — Buses, Trams, Metro & Trains',
        'content': (
            'Public transit is the backbone of any successful CS2 city. Here\'s how to build a system that works.\n\n'
            '## Bus Networks (The Foundation)\n'
            'Buses are your cheapest and most flexible option:\n'
            '- Create circular routes, not point-to-point\n'
            '- Keep stops 2-3 blocks apart\n'
            '- Use bus lanes on busy roads for efficiency\n'
            '- Connect residential areas to transit hubs\n\n'
            '## Trams (Mid-Capacity)\n'
            'Trams are perfect for medium-density corridors:\n'
            '- Higher capacity than buses, lower cost than metro\n'
            '- Best for routes with 2,000-5,000 daily passengers\n'
            '- Can run in the middle of roads or dedicated tracks\n\n'
            '## Metro (High Capacity)\n'
            'For dense urban areas, metro is king:\n'
            '- Stations should be 8-12 blocks apart\n'
            '- Place entrances near major landmarks and commercial zones\n'
            '- A single metro line can remove 500+ cars from roads\n\n'
            '## Train Networks (Regional)\n'
            'Trains connect distant parts of your city:\n'
            '- Use for cargo transport between industrial zones\n'
            '- Passenger trains for suburban commuters\n'
            '- Place stations at the edge of dense areas\n\n'
            '## Pro Tip\n'
            'Always build transit BEFORE traffic gets bad. Retrofitting is much harder.'
        ),
        'category': 'Traffic & Transit',
        'username': 'TransitFan',
        'cover_url': 'https://picsum.photos/seed/cs2-transit/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Top 20 Essential Mods for Cities: Skylines 2 (2026)',
        'content': (
            'The CS2 modding community has created incredible tools. Here are the absolute must-haves.\n\n'
            '## Tier 1: Essential (Get These First)\n'
            '**1. Traffic Manager** — Complete traffic control. Custom lane arrows, speed limits, timed traffic lights.\n'
            '**2. Move It!** — Fine-tune every building, road, and prop position.\n'
            '**3. Fine Road Anarchy** — Place roads anywhere, any angle.\n'
            '**4. Network Multitool** — Create smooth curves and custom intersections.\n\n'
            '## Tier 2: Visual Enhancement\n'
            '**5. Render It!** — Lumen-based global illumination for stunning visuals.\n'
            '**6. Ultimate Level of Detail (ULOD)** — Push LOD distances for crisp views.\n'
            '**7. Skyve** — Realistic clouds, lighting, and atmosphere.\n'
            '**8. Theme Mixer** — Customize terrain colors and textures.\n\n'
            '## Tier 3: Quality of Life\n'
            '**9. 81 Tiles 2** — Unlock entire map for building.\n'
            '**10. Demand Master** — Fine-tune RCI demand.\n'
            '**11. Better Bulldozer** — Delete multiple items with brush sizes.\n'
            '**12. Find It!** — Search for any asset instantly.\n\n'
            '## Tier 4: Gameplay Expansion\n'
            '**13. Plop the Growables** — Manually place any building.\n'
            '**14. Extra Landscaping Tools** — More terrain sculpting options.\n'
            '**15. Pedestrian Zone Expansion** — Enhanced walkability mechanics.\n\n'
            '## Tier 5: Performance\n'
            '**16. FPS Booster** — Disable unnecessary rendering.\n'
            '**17. Render Limits Toggle** — Adjust simulation distances.\n'
            '**18. FPS Limiter** — Cap FPS to reduce GPU load on large cities.\n\n'
            '## Bonus: Must-Have Packs\n'
            '**19. European Suburbia Pack** — More realistic suburban buildings.\n'
            '**20. Japanese City Pack** — Unique Asian architecture.\n\n'
            'All available on Paradox Mods and Thunderstore. Check compatibility before installing!'
        ),
        'category': 'Mods & Modding',
        'username': 'ModMaster',
        'cover_url': 'https://picsum.photos/seed/cs2-mods/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Zoning Secrets — How to Create Beautiful & Functional Districts',
        'content': (
            'Great cities aren\'t just functional — they\'re beautiful. Here\'s how to zone like a pro.\n\n'
            '## Understanding Zone Types\n'
            '**Low Density Residential** — Single-family homes, generates less traffic but lower population.\n'
            '**Medium Density Residential** — Townhouses and small apartments, good balance.\n'
            '**High Density Residential** — Skyscrapers, high population but heavy traffic.\n\n'
            '## The Mixed-Use Approach\n'
            'Don\'t separate residential and commercial completely. Small shops scattered through residential areas:\n'
            '- Reduces commute distances\n'
            '- Creates walkable neighborhoods\n'
            '- Increases property values\n\n'
            '## Grid vs Organic\n'
            'Both work, but each has trade-offs:\n'
            '- **Grid**: Easy to zone, efficient traffic, but can look boring\n'
            '- **Organic**: Beautiful natural look, but harder to manage\n'
            '- **Best approach**: Grid for downtown, organic for suburbs\n\n'
            '## District Specialization\n'
            'Use district policies to shape neighborhoods:\n'
            '- **High-Tech Zone**: Boosts office efficiency\n'
            '- **Tourism District**: Hotels and attractions flourish\n'
            '- **Pedestrian Zone**: No cars, walking and cycling only\n\n'
            '## Green Spaces\n'
            'Parks and plazas aren\'t decorative — they boost land value and citizen happiness. Place a small park every 4-5 blocks.'
        ),
        'category': 'City Planning',
        'username': 'UrbanDesigner',
        'cover_url': 'https://picsum.photos/seed/cs2-zoning/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Water, Power & Sewage — Utility Management Guide',
        'content': (
            'Keeping your city running requires careful utility planning. Here\'s everything you need to know.\n\n'
            '## Power Generation\n'
            '**Early Game:** Wind turbines are cheap but unreliable. Use coal plants for steady base load.\n'
            '**Mid Game:** Solar and geothermal are clean but expensive. Gas plants offer good balance.\n'
            '**Late Game:** Nuclear plants provide massive power. Place them far from residential zones.\n\n'
            '## Water Systems\n'
            '**Fresh Water:** Place water intake pumps upstream from sewage outlets. Never mix them.\n'
            '**Ground Water:** Water towers work for small towns but can deplete.\n'
            '**Water Treatment:** Build treatment plants to reduce pollution.\n\n'
            '## Sewage Management\n'
            '- Place sewage outlets downstream from water intakes\n'
            '- Use water treatment plants to reduce pollution\n'
            '- Inland cities need treatment plants — ocean outlets aren\'t an option\n\n'
            '## Heating\n'
            'CS2 adds heating as a core service. Geothermal plants provide both power and heat. Run heating pipes under roads.\n\n'
            '## Pro Tips\n'
            '- Keep 20-30% extra capacity for growth\n'
            '- Spread power sources across the map (prevents blackouts)\n'
            '- Use the info views to spot coverage gaps\n'
            '- Upgrade utility buildings when available'
        ),
        'category': 'Getting Started',
        'username': 'UtilityPro',
        'cover_url': 'https://picsum.photos/seed/cs2-utilities/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Economy & Budget Mastery — From Deficit to Surplus',
        'content': (
            'Struggling with your city\'s budget? Here\'s how to build a thriving economy.\n\n'
            '## Starting Out: The Deficit Phase\n'
            'Every city starts in debt. That\'s normal. Key strategies:\n'
            '- Take the maximum starting loan (it\'s worth it)\n'
            '- Set service budgets to 50% for the first 1,000 population\n'
            '- Focus on residential zoning to grow your tax base\n\n'
            '## Tax Optimization\n'
            'Default 9% tax rate is good, but you can optimize:\n'
            '- Lowers taxes (7-8%) for residential to attract families\n'
            '- Higher taxes (10-11%) for industrial — they\'ll pay\n'
            '- Adjust individual tax rates based on demand\n\n'
            '## Industrial Strategy\n'
            'Industry is your main early-game revenue source:\n'
            '- Specialize industry for bonus income (Oil, Ore, Farming)\n'
            '- Office zones generate high tax revenue with fewer services\n'
            '- Upgrade to IT Cluster when possible\n\n'
            '## Budget Management\n'
            '- **Education**: Keep at 50% until population > 2,000\n'
            '- **Healthcare**: Small clinic is enough for 3,000 people\n'
            '- **Police/Fire**: One station covers a surprising area\n'
            '- **Roads**: Only upgrade to higher capacity when traffic demands it\n\n'
            '## When to Expand\n'
            'Don\'t expand until:\n'
            '- Your budget is positive for 5+ consecutive months\n'
            '- You have 20%+ spare capacity in all services\n'
            '- Your population demand is 75%+ full\n\n'
            'A balanced budget is the foundation of a great city!'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'Economist',
        'cover_url': 'https://picsum.photos/seed/cs2-economy/800/400',
        'days_ago': 5,
    },
    {
        'title': 'Building Realistic Cities — Detailed Guide for Perfectionists',
        'content': (
            'Want your city to look like the real thing? Here\'s how the pros do it.\n\n'
            '## Start with a Master Plan\n'
            'Before placing your first road, sketch your city layout:\n'
            '- Downtown core near the highway entrance\n'
            '- Industrial zones downwind from residential\n'
            '- Transit corridors following natural terrain\n\n'
            '## Gradual Density Transition\n'
            'Real cities don\'t jump from skyscrapers to farms. Transition gradually:\n'
            '- **Core**: High-density commercial + residential\n'
            '- **Inner ring**: Medium-density mixed use\n'
            '- **Middle ring**: Low-density residential + schools\n'
            '- **Outer ring**: Farms, forestry, rural living\n\n'
            '## Terrain Following\n'
            'Don\'t flatten everything. Roads that follow contours look more natural:\n'
            '- Use "Snap to Terrain" for roads on hills\n'
            '- Terrace steep slopes with retaining walls\n'
            '- Place water features at valley bottoms\n\n'
            '## Detail at Scale\n'
            'The best cities look good at every zoom level:\n'
            '- **Macro**: Clear district boundaries and green belts\n'
            '- **Meso**: Consistent building heights in each zone\n'
            '- **Micro**: Park benches, trees, pedestrian paths\n\n'
            '## Use Real-World References\n'
            'Study Google Maps of real cities. Notice how they handle:\n'
            '- Highway interchanges and exit spacing\n'
            '- Downtown grid patterns vs suburban cul-de-sacs\n'
            '- The relationship between parks and density\n\n'
            'Patience is key — great cities take time to build!'
        ),
        'category': 'City Planning',
        'username': 'UrbanDesigner',
        'cover_url': 'https://picsum.photos/seed/cs2-realistic/800/400',
        'days_ago': 6,
    },
    {
        'title': 'Pollution & Environment — How to Build a Green City',
        'content': (
            'Keep your citizens healthy and your environment clean with these strategies.\n\n'
            '## Understanding Pollution Types\n'
            '**Ground Pollution**: Caused by industry, garbage, and sewage. Spreads through soil and water.\n'
            '**Noise Pollution**: From roads, trains, and commercial zones. Reduces land value nearby.\n'
            '**Air Pollution**: From industrial zones and heavy traffic. Causes citizen sickness.\n\n'
            '## Zoning for Clean Air\n'
            'Always place industrial zones DOWNWIND from residential (check wind direction in info view):\n'
            '- Create a buffer of offices or trees between industry and homes\n'
            '- Use the "Green Industry" policy to reduce pollution\n'
            '- Encourage electric vehicle usage with policies\n\n'
            '## Waste Management\n'
            '- Landfills are cheap but pollute. Place them far from residential\n'
            '- Incineration plants burn garbage and generate power\n'
            '- Recycling centers reduce total waste output\n'
            '- Upgrade to modern waste处理 facilities as soon as possible\n\n'
            '## Green Energy\n'
            '- Solar, wind, and geothermal produce zero pollution\n'
            '- Nuclear is clean but has risks if not maintained\n'
            '- Use the "Green Cities" policy pack for eco-friendly buildings\n\n'
            '## Bonus: The Forest City\n'
            'Plant trees everywhere — along roads, in medians, around buildings. Trees significantly reduce both noise and air pollution. A well-forested city can have 30% lower pollution levels.'
        ),
        'category': 'Tips & Tricks',
        'username': 'EcoBuilder',
        'cover_url': 'https://picsum.photos/seed/cs2-green/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Signature Buildings & Unique Factories — Complete Collection Guide',
        'content': (
            'Signature buildings provide unique bonuses. Here\'s every one you need.\n\n'
            '## How Signature Buildings Work\n'
            'Unlocked by reaching specific milestones or meeting requirements:\n'
            '- Each provides unique city-wide or local bonuses\n'
            '- Some require specific unique factories or resources\n'
            '- Placement matters — some affect only their district\n\n'
            '## Top 10 Must-Get Signature Buildings\n\n'
            '**1. Space Elevator** — Massive tourism boost, requires high population\n'
            '**2. Grand Central Terminal** — Major transit hub, connects all rail lines\n'
            '**3. Medical Research Center** — Boosts healthcare efficiency city-wide\n'
            '**4. International Airport** — Tourism + cargo, requires 50k+ population\n'
            '**5. Opera House** — Entertainment + land value boost\n'
            '**6. Smart Highway** — Automated highway with higher speed limits\n'
            '**7. Geothermal Power Plant** — Unlimited clean energy\n'
            '**8. TV Tower** — Entertainment + unique visual landmark\n'
            '**9. National Park** — Tourism + environment boost\n'
            '**10. Stock Exchange** — Major economic boost for office zones\n\n'
            '## Unique Factories\n'
            'Special industrial buildings that produce unique goods:\n'
            '- **Lemonade Factory**: Requires fruit resources\n'
            '- **Car Manufacturer**: Requires metal + oil\n'
            '- **Electronics Factory**: Requires rare resources\n'
            '- **Clothing Manufacturer**: Requires fiber resources\n\n'
            'Plan your industry around the unique factories available on your map!'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'LandmarkHunter',
        'cover_url': 'https://picsum.photos/seed/cs2-landmarks/800/400',
        'days_ago': 7,
    },
    {
        'title': 'Map Selection Guide — Best Maps for Every Playstyle',
        'content': (
            'The right map makes all the difference. Here\'s a breakdown of every map type.\n\n'
            '## Temperate Maps (Best for Beginners)\n'
            '**Windy Fjords** — Balanced resources, flat terrain near water. Perfect for first city.\n'
            '**Great Highlands** — Mix of flat and hilly terrain. Good for learning road hierarchy.\n'
            '**Emerald Lake** — Large lake in center, great for waterfront builds.\n\n'
            '## Coastal Maps\n'
            '**Azure Gulf** — Beautiful coastline, limited inland space.\n'
            '**Coral Islands** — Archipelago, requires bridges and ferries.\n'
            '**Sandy Shores** — Beachfront, tourism-focused gameplay.\n\n'
            '## Mountain Maps (Advanced)\n'
            '**Alpine Valley** — Steep terrain, terraced building required.\n'
            '**Canyon Cliffs** — Very challenging, limited flat land.\n'
            '**Snowy Peaks** — Winter map, heating is critical.\n\n'
            '## River Maps\n'
            '**Delta Plains** — Multiple river branches, great for canals.\n'
            '**Meander River** — Single large river, natural division.\n'
            '**Creek Crossing** — Small streams, easy water management.\n\n'
            '## Resource-Focused Maps\n'
            '**Mineral Ridge** — Rich in ore and coal. Heavy industry paradise.\n'
            '**Fertile Valley** — Abundant farming resources.\n'
            '**Timberland** — Vast forests for forestry industry.\n\n'
            '## Pro Tip\n'
            'Check the resource map overlay before placing your first road. Building near your primary resource saves massive transit costs later!'
        ),
        'category': 'Getting Started',
        'username': 'MapExplorer',
        'cover_url': 'https://picsum.photos/seed/cs2-maps/800/400',
        'days_ago': 6,
    },
    {
        'title': 'Pedestrian & Cycling Infrastructure — Walkable Cities Guide',
        'content': (
            'The best CS2 cities prioritize people over cars. Here\'s how.\n\n'
            '## Why Walkability Matters\n'
            'Walkable cities have:\n'
            '- Less traffic congestion\n'
            '- Higher land values\n'
            '- Healthier, happier citizens\n'
            '- More vibrant commercial districts\n\n'
            '## Pedestrian Paths\n'
            'Connect key areas with dedicated pedestrian paths:\n'
            '- Shortcuts between cul-de-sacs\n'
            '- Parks and waterfront connections\n'
            '- Direct routes from residential to transit stations\n'
            '- Bridges over busy roads\n\n'
            '## Pedestrian Zones\n'
            'Use the district policy to create car-free zones:\n'
            '- Perfect for historic districts and shopping areas\n'
            '- Boosts local commercial significantly\n'
            '- Requires parking lots at zone boundaries\n\n'
            '## Cycling Infrastructure\n'
            'Bike lanes are cheap and effective:\n'
            '- Add bike lanes to all arterial roads\n'
            '- Create dedicated cycle paths through parks\n'
            '- Bike parking at every transit station\n'
            '- Bike-sharing programs for short trips\n\n'
            '## The 15-Minute City Concept\n'
            'Design neighborhoods where citizens can access all daily needs within 15 minutes of walking:\n'
            '- Small grocery stores in every district\n'
            '- Schools within walking distance\n'
            '- Parks every 4-5 blocks\n'
            '- Medical clinics distributed across the city\n\n'
            'Start with one walkable neighborhood and expand from there!'
        ),
        'category': 'City Planning',
        'username': 'WalkableCity',
        'cover_url': 'https://picsum.photos/seed/cs2-walkable/800/400',
        'days_ago': 8,
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

def seed_data():
    existing = query_db('SELECT COUNT(*) as cnt FROM posts')
    if existing and existing['cnt'] > 3:
        first = query_db('SELECT title FROM posts ORDER BY id ASC LIMIT 1', one=True)
        if first and 'Beginner' in first['title']:
            return
    if existing and existing['cnt'] > 0:
        if DATABASE_URL:
            with get_db().cursor() as cur:
                cur.execute('TRUNCATE TABLE comments CASCADE')
                cur.execute('TRUNCATE TABLE posts CASCADE')
                cur.execute('TRUNCATE TABLE users CASCADE')
        else:
            query_db('DELETE FROM comments')
            query_db('DELETE FROM posts')
            query_db('DELETE FROM users')
    from datetime import timedelta
    base_time = datetime.utcnow()
    for i, post in enumerate(SEED_POSTS):
        try:
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
        except Exception as e:
            import sys, traceback
            print(f'Seed item {i} failed: {post["title"][:40]}... — {e}', file=sys.stderr)
            traceback.print_exc()

with app.app_context():
    init_db()
    try:
        seed_data()
    except Exception as e:
        import sys, traceback
        print(f'Seed data error (non-fatal): {e}', file=sys.stderr)
        traceback.print_exc()

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

    return render_template('index.html', posts=posts, categories=CATEGORIES,
                           get_category_icon=get_category_icon,
                           selected_category=category, search=search,
                           top_users=top_users)

@app.route('/dbcheck')
def dbcheck():
    posts = query_db('SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.id')
    users = query_db('SELECT * FROM users')
    return f'Posts: {len(posts)} — Users: {len(users)} — First post: {posts[0]["title"] if posts else "None"} — Users: {[u["username"] for u in users]}'

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
