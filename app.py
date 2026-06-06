import os, json
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

DATABASE_URL = os.environ.get('DATABASE_URL')
SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'community.db')

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

LANGUAGES = ['en', 'zh', 'de', 'fr', 'ja', 'ko']
TRANSLATIONS = {}

def load_translations():
    for lang in LANGUAGES:
        path = os.path.join(os.path.dirname(__file__), 'translations', f'{lang}.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                TRANSLATIONS[lang] = json.load(f)

load_translations()

def _(key, lang=None):
    if lang is None:
        try:
            lang = session.get('lang', 'en')
        except RuntimeError:
            lang = 'en'
    trans = TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {}))
    return trans.get(key, TRANSLATIONS.get('en', {}).get(key, key))

# Ad Configuration
# Set AD_MODE=adsense + ADSENSE_CLIENT=ca-pub-xxx for Google AdSense
# Set AD_MODE=affiliate (default) for CS2 affiliate banners
# Set AD_MODE=none to disable all ads
# Set HUMBLE_PARTNER=yourid for Humble Bundle affiliate (recommended, up to 15% commission)
#   Sign up: https://www.humblebundle.com/affiliates
AD_MODE = os.environ.get('AD_MODE', 'affiliate').lower()
ADSENSE_CLIENT = os.environ.get('ADSENSE_CLIENT', '')
HUMBLE_PARTNER = os.environ.get('HUMBLE_PARTNER', '')

AD_CONFIG = {
    'mode': AD_MODE,
    'adsense_client': ADSENSE_CLIENT,
    'humble_partner': HUMBLE_PARTNER,
    'enabled': AD_MODE != 'none',
    'steam_url': 'https://store.steampowered.com/app/949230/Cities_Skylines_II/',
    'humble_url': f'https://www.humblebundle.com/store/cities-skylines-ii?partner={HUMBLE_PARTNER}' if HUMBLE_PARTNER else 'https://www.humblebundle.com/store/cities-skylines-ii',
}

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
    {
        'title': 'CS2 Road Building Tricks — Advanced Techniques',
        'content': (
            'Take your road network to the next level with these advanced techniques.'
            ''
            '## Stacked Interchanges'
            'For maximum throughput, build multi-level interchanges. Use elevated roads and tunnels to separate traffic flows:'
            '- Stack interchanges save space in dense downtown areas'
            '- Use the Elevated Road tool to create ramps above surface streets'
            '- Tunnels preserve surface-level pedestrian access'
            ''
            '## Merging and Diverging'
            'When merging traffic, use longer merge lanes. Short merges create bottlenecks. A good merge lane is 8-12 cells long.'
            ''
            '## Grade-Separated Intersections'
            'Eliminate intersections entirely using bridges and tunnels. Highways should have zero intersections.'
            ''
            '## One-Way Couplet Streets'
            'Pair two one-way streets running opposite directions. This doubles throughput vs two-way streets.'
        ),
        'category': 'Traffic & Transit',
        'username': 'RoadEngineer',
        'cover_url': 'https://picsum.photos/seed/cs2-roaden1/800/400',
        'days_ago': 1,
    },
    {
        'title': 'How to Make Money Fast — Early Game Economy',
        'content': (
            'Struggling with debt early game? Here are proven strategies.'
            ''
            '## The First 30 Minutes'
            '- Take the maximum starting loan'
            '- Set all service budgets to 50% immediately'
            '- Zone only residential + a tiny bit of commercial'
            "- Don't build schools until population > 1,000"
            ''
            '## Tax Tweaks'
            '- Keep residential at 8% to attract families'
            '- Raise industrial to 11%'
            '- Commercial at 9% is the sweet spot'
            ''
            '## Industry Advantage'
            'Zone industry near highway access. Specialize in available natural resources for bonus income.'
            ''
            '## When to Expand'
            'Only expand when budget has been positive for 5+ consecutive months and you have 20%+ spare capacity.'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'MoneyMaker',
        'cover_url': 'https://picsum.photos/seed/cs2-moneym2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Roundabout Design Guide — Every Pattern Explained',
        'content': (
            'Roundabouts are the single most effective traffic solution in CS2.'
            ''
            '## Basic Roundabout (2-Lane)'
            'Perfect for residential-collector intersections:'
            '- 3-4 cell radius with 2-lane roads'
            '- Works up to 1,000 vehicles per hour'
            ''
            '## Medium Roundabout (4-Lane)'
            'For collector-arterial intersections:'
            '- 5-6 cell radius with 4-lane roads'
            '- Add dedicated slip lanes for right turns'
            '- Handles 2,000-4,000 vehicles per hour'
            ''
            '## Large Turbo Roundabout'
            'For arterial-highway connections:'
            '- Multi-lane with spiral markings'
            '- Use one-way roads for circulatory lanes'
            '- Handles 6,000+ vehicles per hour'
            ''
            'Never place buildings too close to a roundabout entrance — vehicles slow and get blocked.'
        ),
        'category': 'Traffic & Transit',
        'username': 'RoundaboutPro',
        'cover_url': 'https://picsum.photos/seed/cs2-rounda3/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Dealing with Death Waves — A Complete Guide',
        'content': (
            'Death waves are one of the most frustrating mechanics in CS2.'
            ''
            '## What Causes Death Waves?'
            'Zoning large residential areas at once makes all residents the same age. They die simultaneously ~60 years later.'
            ''
            '## Prevention'
            '- Zone residential in small batches (500-1,000 units at a time)'
            '- Space out zoning by a few in-game months'
            '- Mix high, medium, and low density to stagger ages'
            ''
            '## During a Wave'
            '- Increase healthcare budget to 120%'
            '- Build additional medical clinics'
            '- Add extra crematoriums'
            '- Wave passes after about 6 in-game months'
            ''
            'A city growing 500 residents per month will never experience death waves.'
        ),
        'category': 'Tips & Tricks',
        'username': 'HealthyCity',
        'cover_url': 'https://picsum.photos/seed/cs2-health1/800/400',
        'days_ago': 1,
    },
    {
        'title': 'How to Build a Perfect Downtown',
        'content': (
            'A great downtown is the heart of any city.'
            ''
            '## The Downtown Grid'
            '- Use 6x12 or 8x16 cell blocks for optimal building sizes'
            '- Main streets every 4 blocks should be 4-lane or 6-lane'
            '- Side streets can be 2-lane one-way'
            ''
            '## Mixed-Use Core'
            '- Ground floor commercial, upper floor residential/office'
            '- Scatter small parks between buildings'
            '- Place signature buildings as landmarks'
            ''
            '## Transit Integration'
            '- Metro station every 8-10 blocks'
            '- Bus stops every 2-3 blocks'
            '- Central transit hub near city hall'
            ''
            '## Density Transition'
            'Highest density at center, gradually decreasing outward.'
        ),
        'category': 'City Planning',
        'username': 'DowntownDev',
        'cover_url': 'https://picsum.photos/seed/cs2-downto5/800/400',
        'days_ago': 5,
    },
    {
        'title': 'Suburban Planning Guide — Realistic Neighborhoods',
        'content': (
            'Build beautiful, functional suburbs.'
            ''
            '## Cul-de-Sac Design'
            '- Branch cul-de-sacs off collector roads'
            '- Keep each cul-de-sac to 8-12 houses'
            '- Connect them with pedestrian paths'
            ''
            '## School Placement'
            'Elementary schools within walking distance (8-10 blocks) of every residential area.'
            ''
            '## Parks and Green Spaces'
            '- Small playground every 4-5 blocks'
            '- Medium park per district'
            '- Large nature reserve on the outskirts'
            ''
            '## The Commuter Problem'
            'Suburbs generate commuters. Ensure good road connections to downtown. Build a commuter train station.'
        ),
        'category': 'City Planning',
        'username': 'SuburbKing',
        'cover_url': 'https://picsum.photos/seed/cs2-suburb4/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Disaster Management — Prepare for the Worst',
        'content': (
            "CS2 can throw disasters at your city. Here's how to prepare."
            ''
            '## Early Warning'
            '- Build Emergency Broadcast Center as soon as available'
            '- Place disaster warning systems in every district'
            '- Plan evacuation routes to open areas'
            ''
            '## Fire and Rescue'
            '- Helicopter depots cover large areas quickly'
            '- Place fire stations in high-value districts'
            '- Maintain 80%+ coverage of all buildings'
            ''
            '## Post-Disaster Recovery'
            '- Keep extra budget in reserve for repairs'
            '- Road maintenance depots speed up repairs'
            '- Rebuild damaged parks and services first'
            ''
            'A prepared city recovers in days. An unprepared one takes months.'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'SafetyFirst',
        'cover_url': 'https://picsum.photos/seed/cs2-safety6/800/400',
        'days_ago': 6,
    },
    {
        'title': 'How to Build Highways That Actually Work',
        'content': (
            'Highways are the backbone of your regional transport. Get them right.'
            ''
            '## Proper Interchange Spacing'
            'Leave at least 60 cells between full-size highway interchanges. Too-close exits create weaving problems.'
            ''
            '## Highway Exit Design'
            '- Use longer deceleration lanes (12+ cells)'
            '- Never have exits on the left side'
            '- Stack interchanges save space in dense areas'
            ''
            '## The Diamond Interchange'
            'The most reliable design: 4 ramps, diamond pattern. Cheap and easy to upgrade.'
            ''
            '## Avoiding Highway Gridlock'
            'Never let local streets connect directly to highways — always use interchanges.'
        ),
        'category': 'Traffic & Transit',
        'username': 'HighwayHero',
        'cover_url': 'https://picsum.photos/seed/cs2-highwa2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Landscaping Guide — Make Your City Beautiful',
        'content': (
            'The best CS2 cities are beautiful as well as functional.'
            ''
            '## Terrain Sculpting'
            '- Create hills, valleys, and waterfronts'
            '- Avoid flattening everything — natural terrain looks better'
            '- Create retaining walls on steep slopes'
            ''
            '## Tree Placement'
            '- Trees reduce noise and air pollution'
            '- Line major roads with trees for visual appeal'
            '- Create forested areas in parks and green belts'
            ''
            '## Water Features'
            '- Canals add charm to downtown areas'
            '- Waterfront promenades increase property values'
            '- Ponds create natural park centers'
            ''
            '## Lighting'
            'Good lighting makes nighttime cities magical.'
        ),
        'category': 'Tips & Tricks',
        'username': 'GardenCity',
        'cover_url': 'https://picsum.photos/seed/cs2-garden7/800/400',
        'days_ago': 7,
    },
    {
        'title': 'Office Zone Strategy — Build a Tech Economy',
        'content': (
            'Office zones are the key to a wealthy, low-pollution city.'
            ''
            '## Why Offices Matter'
            '- High tax revenue with minimal services'
            '- Zero pollution'
            '- Fewer traffic trips than industry'
            ''
            '## The Education Pipeline'
            '- Elementary schools in every residential area'
            '- High schools per 5,000 population'
            '- Universities before 20,000 population'
            ''
            '## IT Cluster Specialization'
            'Transforms offices into tech hubs. Requires graduates. Boosts tax income by 25%.'
            ''
            '## Placement Tips'
            'Place offices between residential and industrial as a buffer zone.'
        ),
        'category': 'City Planning',
        'username': 'TechBro',
        'cover_url': 'https://picsum.photos/seed/cs2-techbr3/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Park Life — Every Park Type Explained',
        'content': (
            "Parks aren't just decoration — they're essential infrastructure."
            ''
            '## Small Parks'
            '- Gardens, playgrounds, small plazas'
            '- Place every 4-5 blocks in residential areas'
            '- Boost land value in a small radius'
            ''
            '## Medium Parks'
            '- Dog parks, sports fields, botanical gardens'
            '- One per district is a good rule'
            '- Attract visitors from nearby commercial'
            ''
            '## Large Parks'
            '- Nature reserves, amusement parks, zoos'
            '- Major tourist attractions'
            '- City-wide happiness boost'
            ''
            'A well-parked city has 15-20% higher land values.'
        ),
        'category': 'City Planning',
        'username': 'ParkRanger',
        'cover_url': 'https://picsum.photos/seed/cs2-parkra5/800/400',
        'days_ago': 5,
    },
    {
        'title': 'Noise Pollution Solutions — Quiet City Guide',
        'content': (
            'Noise pollution is one of the most overlooked issues in CS2.'
            ''
            '## Sources of Noise'
            '- Roads (especially highways and 6-lane roads)'
            '- Commercial zones (especially at night)'
            '- Industrial areas'
            '- Airports and train stations'
            ''
            '## Mitigation Strategies'
            '- Use trees along roads — they absorb noise'
            '- Create office buffer zones'
            '- Ban heavy traffic in residential districts'
            '- Use sound barriers along highways'
            ''
            '## Quiet Zone District Policy'
            'Create quiet districts. Citizens pay higher taxes for peace.'
        ),
        'category': 'Tips & Tricks',
        'username': 'PeacefulCity',
        'cover_url': 'https://picsum.photos/seed/cs2-peacef4/800/400',
        'days_ago': 4,
    },
    {
        'title': 'How to Use District Policies Like a Pro',
        'content': (
            'District policies are powerful tools that many players ignore.'
            ''
            '## Must-Use Policies'
            '- Heavy Traffic Ban: Removes trucks from residential areas'
            '- Old Town: Stops new buildings, preserves historic areas'
            '- Free Public Transport: Boosts transit usage by 300%'
            '- Recycling: Reduces garbage output by 50%'
            ''
            '## Revenue Policies'
            '- Big Business Benefactor: Commercial pays extra'
            '- Tourist District: Hotels get bonus income'
            '- High-Tech Zone: Office tax bonus'
            ''
            '## Social Policies'
            '- Smoking Ban: Healthier citizens, fewer medical visits'
            '- Sports and Health: Citizens live longer'
            '- Night Vibe: Entertainment districts thrive at night'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'PolicyWonk',
        'cover_url': 'https://picsum.photos/seed/cs2-policy2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Education System Guide — From K to University',
        'content': (
            'Education is the key to a prosperous city.'
            ''
            '## The Education Chain'
            '- Elementary: 1 per 2,000 population'
            '- High school: 1 per 8,000 population'
            '- University: 1 per 20,000 population'
            ''
            '## Education Benefits'
            '- Educated workers = more offices, less industry'
            '- Higher education = higher tax revenue'
            '- Reduces crime, improves healthcare'
            ''
            '## University Specializations'
            '- Business School: Boosts commercial tax'
            '- Engineering School: Improves industrial efficiency'
            '- Medical School: City-wide healthcare boost'
            '- Law School: Reduces crime rates'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'Professor',
        'cover_url': 'https://picsum.photos/seed/cs2-profes2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Healthcare Guide — Keep Citizens Healthy',
        'content': (
            'A healthy city is a happy city.'
            ''
            '## Healthcare Facilities'
            '- Medical Clinic: Handles up to 3,000 people'
            '- Hospital: Handles up to 15,000 people'
            '- Crematorium: Essential for death management'
            ''
            '## Coverage Planning'
            'Clinics every 15-20 blocks. Use info view to spot gaps.'
            ''
            '## Pollution and Health'
            'Citizens near industry or busy roads get sick. Plant trees to reduce illness.'
            ''
            '## Ambulance Management'
            'Good roads save lives. Ensure stations access arterial roads.'
            ''
            "Don't overbuild — match capacity to population."
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'DocBrown',
        'cover_url': 'https://picsum.photos/seed/cs2-docbro3/800/400',
        'days_ago': 3,
    },
    {
        'title': 'The Complete Industry Guide',
        'content': (
            'Industry is the engine of your economy.'
            ''
            '## Generic Industry'
            'Start here. Zone with highway access, buffer from residential.'
            ''
            '## Specialized Industry'
            '- Farming: Low pollution, needs fertile land'
            '- Forestry: Medium income, needs forests'
            '- Oil: High income, high pollution'
            '- Ore: High income, high pollution'
            ''
            '## Office Upgrades'
            'Educated citizens upgrade industry to offices. Build schools.'
            ''
            '## Cargo Transport'
            'Build cargo train stations near industry to reduce truck traffic.'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'FactoryKing',
        'cover_url': 'https://picsum.photos/seed/cs2-factor4/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Bridge and Tunnel Design',
        'content': (
            'Bridges and tunnels are essential for difficult terrain.'
            ''
            '## Bridge Types'
            '- Flat: Cheapest, short spans'
            '- Arch: Medium, longer spans'
            '- Suspension: Expensive, very wide gaps'
            ''
            '## Tunnel Best Practices'
            '- Preserve surface aesthetics'
            '- More expensive but space-saving'
            '- Pedestrian tunnels connect districts safely'
            ''
            '## Height Management'
            'Use Page Up/Down before placing for precision.'
            ''
            'Make them beautiful — add lighting and parks at entrances.'
        ),
        'category': 'Tips & Tricks',
        'username': 'BridgeBuilder',
        'cover_url': 'https://picsum.photos/seed/cs2-bridge5/800/400',
        'days_ago': 5,
    },
    {
        'title': 'Tourism Guide — Attract Visitors',
        'content': (
            'Tourism is a powerful revenue source.'
            ''
            '## Tourist Attractions'
            '- Signature buildings (Space Elevator, Opera House)'
            '- Natural wonders and parks'
            '- Entertainment districts with nightlife'
            ''
            '## Tourist Transport'
            'Tourists arrive via trains, airports, harbors, and highways.'
            ''
            '## Tourism Infrastructure'
            '- Hotels near attractions'
            '- Public transport for visitors'
            '- Parks and plazas as gathering spots'
            ''
            '## Tourism District Policy'
            'Enable in hotel areas for bonus income.'
        ),
        'category': 'Guides & Walkthroughs',
        'username': 'TravelGuide',
        'cover_url': 'https://picsum.photos/seed/cs2-travel2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Waterfront Development Guide',
        'content': (
            'Waterfront property is the most valuable real estate.'
            ''
            '## Quays and Canals'
            '- Define edges with quays'
            '- Canals add charm and increase land values'
            '- Pedestrian bridges create photo-worthy spots'
            ''
            '## Beach Development'
            '- Beaches attract tourists and residents'
            '- Build promenades with shops'
            '- Add volleyball courts and playgrounds'
            ''
            '## Flood Management'
            'Check flood maps before building. Use flood walls.'
        ),
        'category': 'City Planning',
        'username': 'CoastalDev',
        'cover_url': 'https://picsum.photos/seed/cs2-coasta6/800/400',
        'days_ago': 6,
    },
    {
        'title': 'Performance Optimization — Smooth CS2',
        'content': (
            'Large cities can bring powerful PCs to their knees.'
            ''
            '## Graphics Settings'
            '- Lower shadow quality (biggest impact)'
            '- Reduce LOD distance'
            '- Disable ambient occlusion'
            ''
            '## Mod Performance'
            '- Loading Screen Mod reduces RAM'
            '- FPS Booster disables unnecessary rendering'
            ''
            '## City Design for Performance'
            '- Fewer unique buildings = better FPS'
            '- Reduce tree count in dense areas'
            '- Keep population under 200k for smooth gameplay'
            ''
            '- Restart every 2-3 hours'
            '- Clear asset cache periodically'
        ),
        'category': 'Tips & Tricks',
        'username': 'Optimizer',
        'cover_url': 'https://picsum.photos/seed/cs2-optimi3/800/400',
        'days_ago': 3,
    },
    {
        'title': 'Fixing Common CS2 Bugs',
        'content': (
            "CS2 has its share of bugs. Here's how to fix them."
            ''
            '## No Pedestrian Access'
            '- Check pedestrian path connections'
            '- Ensure crosswalks across busy roads'
            ''
            '## High Rent / No Customers'
            '- Balance land values with zone types'
            '- Use the Renter and Land Value Policy mod'
            ''
            '## General Fixes'
            '- Verify game files on Steam'
            '- Clear asset cache'
            '- Remove recently added mods'
            '- Update graphics drivers'
        ),
        'category': 'Tips & Tricks',
        'username': 'BugFixer',
        'cover_url': 'https://picsum.photos/seed/cs2-bugfix2/800/400',
        'days_ago': 2,
    },
    {
        'title': 'Night City — Urban Design After Dark',
        'content': (
            'Night mode changes gameplay. Build for the dark.'
            ''
            '## Lighting Strategy'
            '- Street lights for pedestrian safety'
            '- Parks need lighting to stay open'
            '- Commercial benefits from decorative lighting'
            ''
            '## Night Economy'
            '- Entertainment districts thrive at night'
            '- Night bus routes serve shift workers'
            ''
            '## Crime Management'
            'Crime increases at night. More police coverage needed.'
            ''
            '## Night Tourism'
            'Build entertainment districts, night markets, observation decks.'
        ),
        'category': 'City Planning',
        'username': 'NightOwl',
        'cover_url': 'https://picsum.photos/seed/cs2-nighto4/800/400',
        'days_ago': 4,
    },
    {
        'title': 'Mod Installation Guide — Get Started with Mods',
        'content': (
            "New to modding? Here's how to install mods safely."
            ''
            '## Where to Get Mods'
            '- Paradox Mods: Official, integrated'
            '- Thunderstore: Community-driven, easy installer'
            '- Steam Workshop: For CS1 only'
            ''
            '## Installation Steps'
            '- Download via Paradox Mods launcher'
            '- Enable mods before loading your save'
            '- Check compatibility in the mod description'
            ''
            '## Safety Tips'
            '- Backup saves before installing'
            '- Install one mod at a time'
            '- Read comments for known issues'
            '- Remove unused mods to prevent conflicts'
            ''
            'Start small. Add mods as you need them.'
        ),
        'category': 'Mods & Modding',
        'username': 'ModMaster',
        'cover_url': 'https://picsum.photos/seed/cs2-modmas1/800/400',
        'days_ago': 1,
    },
    {
        'title': 'Map Review — Best Maps Compared',
        'content': (
            "Can't pick a map? Here's how each type plays."
            ''
            '## Temperate (Best for Beginners)'
            '- Windy Fjords: Balanced, flat terrain'
            '- Great Highlands: Mix of flat and hills'
            ''
            '## Coastal Maps'
            '- Azure Gulf: Beautiful coastline'
            '- Coral Islands: Archipelago, needs bridges'
            ''
            '## Mountain (Advanced)'
            '- Alpine Valley: Steep, terraced building'
            '- Snowy Peaks: Winter, heating critical'
            ''
            '## River Maps'
            '- Delta Plains: Multiple river branches'
            '- Meander River: Natural city division'
            ''
            '## Pro Tip'
            'Check resource overlay before placing first road.'
        ),
        'category': 'Getting Started',
        'username': 'MapExplorer',
        'cover_url': 'https://picsum.photos/seed/cs2-mapexp6/800/400',
        'days_ago': 6,
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
                    created_at TEXT NOT NULL,
                    lang TEXT DEFAULT 'en'
                )
            ''')
            cur.execute("ALTER TABLE posts ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'en'")
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
                lang TEXT DEFAULT 'en',
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
    existing = query_db('SELECT COUNT(*) as cnt FROM posts', one=True)
    if existing and existing['cnt'] > 3:
        first = query_db('SELECT title FROM posts ORDER BY id ASC LIMIT 1', one=True)
        if first and 'CS2' in first['title']:
            return
    if existing and existing['cnt'] > 0:
        query_db('DELETE FROM comments')
        query_db('DELETE FROM posts')
        query_db('DELETE FROM users')
    from datetime import timedelta
    base_time = datetime.utcnow()
    for i, post in enumerate(SEED_POSTS):
        user = query_db('SELECT id FROM users WHERE username = ?', (post['username'],), one=True)
        if not user:
            query_db('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                     (post['username'], 'guide123', (base_time - timedelta(days=post['days_ago'] + 1)).isoformat() + 'Z'))
            user = query_db('SELECT id FROM users WHERE username = ?', (post['username'],), one=True)
        created = (base_time - timedelta(days=post['days_ago'])).isoformat() + 'Z'
        for lang_code in LANGUAGES:
            query_db(
                "INSERT INTO posts (title, content, category, cover_url, user_id, created_at, lang) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (post['title'], post['content'], post['category'], post['cover_url'], user['id'], created, lang_code)
            )

with app.app_context():
    init_db()
    try:
        seed_data()
    except Exception as e:
        import sys
        print(f'Seed data error (non-fatal): {e}', file=sys.stderr)

def now():
    return datetime.utcnow().isoformat() + 'Z'

def get_category_icon(category):
    return CATEGORY_ICONS.get(category, '📋')

@app.context_processor
def inject_globals():
    return dict(lang=getattr(g, 'lang', 'en'), _=lambda key: _(key, getattr(g, 'lang', 'en')), LANGUAGES=LANGUAGES, ad=AD_CONFIG)

@app.before_request
def load_user():
    g.user = None
    g.lang = session.get('lang', 'en')
    user_id = session.get('user_id')
    if user_id:
        g.user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)

@app.route('/lang/<code>')
def set_lang(code):
    if code in LANGUAGES:
        session['lang'] = code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('q', '').strip()
    lang = g.lang

    query = '''
        SELECT p.*, u.username,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
        FROM posts p JOIN users u ON p.user_id = u.id
    '''
    conditions = []
    params = []

    conditions.append("(p.lang = ? OR p.lang = '' OR p.lang IS NULL)")
    params.append(lang)

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
    featured = query_db('''
        SELECT p.*, u.username,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
        FROM posts p JOIN users u ON p.user_id = u.id
        WHERE p.lang = ?
        ORDER BY p.created_at DESC LIMIT 4
    ''', (lang,))
    top_users = query_db('''
        SELECT u.id, u.username, COUNT(p.id) as post_count
        FROM users u LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id ORDER BY post_count DESC LIMIT 5
    ''')

    return render_template('index.html', posts=posts, featured=featured, categories=CATEGORIES,
                           get_category_icon=get_category_icon,
                           selected_category=category, search=search,
                           top_users=top_users, lang=lang, _=_)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash(_('flash.required_fields'))
            return render_template('register.html')
        try:
            query_db('INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                     (username, password, now()))
            user = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
            session['user_id'] = user['id']
            flash(_('flash.welcome'))
            return redirect(url_for('index'))
        except Exception:
            flash(_('flash.register_error'))
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
            flash(_('flash.welcome_back'))
            return redirect(url_for('index'))
        flash(_('flash.login_error'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash(_('flash.logged_out'))
    return redirect(url_for('index'))

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    if not g.user:
        flash(_('flash.login_first'))
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        category = request.form['category']
        cover_url = request.form.get('cover_url', '').strip()
        if not title or not content:
            flash(_('flash.required_fields'))
            return render_template('new_post.html', categories=CATEGORIES, get_category_icon=get_category_icon)
        query_db("INSERT INTO posts (title, content, category, cover_url, user_id, created_at, lang) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (title, content, category, cover_url, g.user['id'], now(), g.lang))
        flash(_('flash.post_created'))
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
        flash(_('flash.post_not_found'))
        return redirect(url_for('index'))

    if request.method == 'POST' and g.user:
        content = request.form['content'].strip()
        if content:
            query_db('INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
                     (post_id, g.user['id'], content, now()))
            flash(_('flash.comment_added'))
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
        flash(_('flash.user_not_found'))
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
