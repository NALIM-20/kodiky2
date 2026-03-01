import requests
from flask import Flask, request
import random
import hashlib

app = Flask(__name__)

BASE_SEARCH_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s="
FILTER_URL = "https://www.thecocktaildb.com/api/json/v1/1/filter.php?i="

INGREDIENTS_MENU = ["Vodka","Rum","Gin","Tequila","Whiskey","Triple Sec","Liqueur","Brandy","Cognac","Vermouth"]

INFO_BUBBLES = [
    "Classic Martini invented in late 1800s",
    "Try Grey Goose Vodka for smooth cocktails",
    "Bacardi Rum is perfect for Mojitos",
    "Fun fact: The Margarita is named after a woman",
    "Gin and tonic was originally medicinal",
    "Triple Sec adds sweet citrus flavor",
    "Use fresh herbs for amazing flavor",
    "Old Fashioned is a whiskey classic",
    "Tequila sunrise looks stunning with orange juice",
    "Brandy is perfect for warming cocktails"
]

FUN_FACTS = [
    "Martini invented in the late 1800s",
    "Margarita named after a woman",
    "Gin and tonic was originally medicinal",
    "Use fresh herbs for amazing flavor",
    "Tequila sunrise looks stunning with orange juice",
    "Old Fashioned is a whiskey classic",
    "Try Grey Goose for smooth cocktails",
    "Bacardi Rum is perfect for Mojitos"
]

def get_cocktails(search="", ingredients=[]):
    cocktails = []
    if ingredients:
        all_ids = set()
        for ing in ingredients:
            resp = requests.get(FILTER_URL + ing)
            if resp.status_code == 200:
                drinks = resp.json().get("drinks")
                if drinks:
                    all_ids.update(d['idDrink'] for d in drinks)
        for cid in all_ids:
            detail_resp = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={cid}")
            if detail_resp.status_code == 200:
                cocktails.append(detail_resp.json()['drinks'][0])
    elif search:
        resp = requests.get(BASE_SEARCH_URL + search)
        if resp.status_code == 200:
            drinks = resp.json().get("drinks")
            if drinks:
                cocktails.extend(drinks)
    else:
        for letter in "abcdefghijklmnopqrstuvwxyz":
            resp = requests.get(BASE_SEARCH_URL + letter)
            if resp.status_code == 200:
                drinks = resp.json().get("drinks")
                if drinks:
                    cocktails.extend(drinks)
    return cocktails

def get_info_for_cocktail(name):
    index = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(INFO_BUBBLES)
    return INFO_BUBBLES[index]

@app.route("/")
def home():
    search_query = request.args.get("search", "").strip()
    ingredient_filter = request.args.getlist("ingredient")
    cocktails = get_cocktails(search=search_query, ingredients=ingredient_filter)

    cards = ""
    modals = ""

    # Determine if we are showing search/filter results
    show_search_results = bool(search_query or ingredient_filter)

    if show_search_results:
        display_cards = cocktails  # Only show static cards for search/filter
    else:
        inspiration_count = max(5, min(len(cocktails), 10))
        display_cards = random.sample(cocktails, inspiration_count) if cocktails else []

    for idx, drink in enumerate(display_cards):
        name = drink.get("strDrink", "Unknown")
        image = drink.get("strDrinkThumb", "")

        ingredients_list = []
        for i in range(1,16):
            ing = drink.get(f"strIngredient{i}")
            measure = drink.get(f"strMeasure{i}")
            if ing:
                ingredients_list.append(f"{measure.strip()+' ' if measure else ''}{ing.strip()}")
        ingredient_text = "<br>".join(ingredients_list)
        instructions = drink.get("strInstructions", "No instructions available")

        bubble_text = get_info_for_cocktail(name)

        cards += f"""
        <div class="card neon" onclick="openModal('modal{idx}')">
            <img src="{image}" alt="{name}">
            <h3>{name}</h3>
            <div class="info-bubble neon">{bubble_text}</div>
        </div>
        """

        modals += f"""
        <div id="modal{idx}" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('modal{idx}')">&times;</span>
                <h2>{name}</h2>
                <img src="{image}" style="width:200px;margin:10px 0;">
                <h3>Ingredients:</h3>
                <p>{ingredient_text}</p>
                <h3>Instructions:</h3>
                <p>{instructions}</p>
            </div>
        </div>
        """

    ingredient_buttons = ""
    for ing in INGREDIENTS_MENU:
        active = "style='background:#ffaa33;color:black;'" if ing in ingredient_filter else ""
        ingredient_buttons += f"""<button onclick="toggleIngredient('{ing}')" {active}>{ing}</button>"""

    main_text = """
    <p style="text-align:center;max-width:800px;margin:auto;font-size:16px;color:#ffaa33;">
    Explore cocktails for inspiration. Did you know the Martini was invented in the late 1800s? 
    We recommend top-quality brands like Grey Goose Vodka, Bacardi Rum, and Bombay Sapphire Gin.
    Enjoy responsibly and get inspired!
    </p>
    """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Neon Cocktail Dashboard</title>
        <style>
            body {{ margin:0;padding:20px;font-family:Arial;background:black;color:#ff7a00; position:relative; overflow-x:hidden; }}
            body::before {{
                content:"";
                position:fixed; top:0; left:0; width:100%; height:100%;
                background: radial-gradient(circle at 50% 50%, rgba(255,170,51,0.05), transparent 70%);
                animation: backgroundPulse 6s infinite alternate;
                pointer-events:none;
            }}
            @keyframes backgroundPulse {{
                0% {{opacity:0.05;}}
                50% {{opacity:0.12;}}
                100% {{opacity:0.05;}}
            }}
            h1 {{ text-align:center;font-size:40px;margin-bottom:10px;text-shadow:0 0 10px #ff7a00,0 0 20px #ff7a00,0 0 30px #ffaa33; }}
            #funFacts {{ text-align:center;font-size:18px;color:#ffaa33;margin-bottom:15px;text-shadow:0 0 5px #ff7a00; }}
            .main-text {{ margin-bottom:20px; }}
            .search-container {{ text-align:center;margin-bottom:10px; }}
            input {{ padding:10px;width:200px;border-radius:6px;border:1px solid #ff7a00;background:blac    k;color:#ff7a00; }}
            input::placeholder {{ color:#ffaa33; }}
            .ingredient-menu {{ text-align:center;margin:15px 0; }}
            .ingredient-menu button {{ padding:8px 12px;margin:3px;border:none;border-radius:6px;background:#ff7a00;color:black;cursor:pointer;font-weight:bold; }}
            .ingredient-menu button:hover {{ background:#ffaa33; }}
            .carousel-container {{ display:flex;overflow:hidden;gap:15px;margin-top:20px; }}
            .carousel-track {{ display:flex;gap:15px; }}
            .card {{ background:#111;border:2px solid #ff7a00;border-radius:12px;padding:10px;text-align:center;width:150px;flex-shrink:0;transition:transform 0.3s ease, box-shadow 0.3s ease; }}
            .card:hover {{ transform: scale(1.05); box-shadow:0 0 30px #ffaa33, 0 0 50px #ff7a00; }}
            .card img {{ width:100%;height:150px;object-fit:cover;border-radius:8px;margin-bottom:5px; }}
            .card h3 {{ margin:0;font-size:14px;text-shadow:0 0 5px #ff7a00, 0 0 10px #ffaa33; }}
            .info-bubble {{ background:#ff7a00;color:black;font-size:12px;border-radius:6px;padding:4px;margin-top:5px;text-align:center; text-shadow:0 0 5px #ff7a00; }}
            .neon {{ animation: flicker 2s infinite alternate; }}
            @keyframes flicker {{
                0% {{ text-shadow: 0 0 5px #ff7a00,0 0 10px #ffaa33; }}
                50% {{ text-shadow: 0 0 10px #ff7a00,0 0 20px #ffaa33; }}
                100% {{ text-shadow: 0 0 5px #ff7a00,0 0 10px #ffaa33; }}
            }}
            .modal {{ display:none;position:fixed;z-index:100;left:0;top:0;width:100%;height:100%;overflow:auto;background-color:rgba(0,0,0,0.9); }}
            .modal-content {{ background:#111;margin:5% auto;padding:20px;border:2px solid #ff7a00;width:80%;max-width:600px;border-radius:12px;color:#ff7a00; }}
            .modal-content h2 {{ margin-top:0;text-align:center; }}
            .modal-content p {{ line-height:1.4; }}
            .close {{ color:#ff7a00;float:right;font-size:28px;font-weight:bold;cursor:pointer; }}
            .close:hover {{ color:#ffaa33; }}
        </style>
    </head>
    <body>
        <h1>🍹 Neon Cocktail</h1>
        <div id="funFacts"></div>
        <div class="main-text">{main_text}</div>

        <div class="search-container">
            <form method="get" id="searchForm">
                <input type="text" name="search" placeholder="Search by name..." value="{search_query}">
                <button type="submit">Search</button>
            </form>
        </div>

        <!-- Recommended brands -->
        <div style="text-align:center;margin:10px 0;color:#ffaa33;font-size:14px;text-shadow:0 0 3px #ff7a00;">
            Recommended brands: Grey Goose Vodka, Bacardi Rum, Bombay Sapphire Gin, Cointreau, Maker's Mark Whiskey
        </div>

        {"<div class='carousel-container'><div class='carousel-track' id='carouselTrack'>" + cards + "</div></div>" if not show_search_results else "<div style='display:flex;flex-wrap:wrap;gap:15px;justify-content:center;'>" + cards + "</div>"}

        {modals}

        <script>
            function openModal(id) {{ document.getElementById(id).style.display='block'; }}
            function closeModal(id) {{ document.getElementById(id).style.display='none'; }}
            window.onclick = function(event) {{
                var modals=document.getElementsByClassName('modal');
                for(var i=0;i<modals.length;i++){{ if(event.target==modals[i]){{modals[i].style.display='none';}} }}
            }}

            function toggleIngredient(ingredient){{
                let params = new URLSearchParams(window.location.search);
                let current = params.getAll('ingredient');
                if(current.includes(ingredient)){{
                    current = current.filter(i=>i!==ingredient);
                }} else {{
                    current.push(ingredient);
                }}
                params.delete('ingredient');
                current.forEach(i=>params.append('ingredient',i));
                window.location.search = params.toString();
            }}

            // Rotate fun facts
            const facts = {FUN_FACTS};
            let factIndex = 0;
            function rotateFacts() {{
                document.getElementById('funFacts').innerText = facts[factIndex];
                factIndex = (factIndex + 1) % facts.length;
            }}
            rotateFacts();
            setInterval(rotateFacts, 5000);

            if(!{str(show_search_results).lower()}) {{
                const track = document.getElementById('carouselTrack');
                let scrollAmount = 0;
                const speed = 1;
                if(track.children.length>0){{
                    track.innerHTML += track.innerHTML;
                    function animateCarousel(){{
                        scrollAmount += speed;
                        if(scrollAmount >= track.scrollWidth/2) scrollAmount = 0;
                        track.style.transform = 'translateX(-'+scrollAmount+'px)';
                        requestAnimationFrame(animateCarousel);
                    }}
                    animateCarousel();
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_template

if __name__ == "__main__":
    app.run(debug=True)