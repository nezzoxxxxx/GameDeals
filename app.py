
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

st.set_page_config(
    page_title="GameDeals",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 GameDeals")
st.subheader("Découvre des jeux gratuitement !")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Recherche
recherche = st.text_input(
    "🔍 Rechercher un jeu",
    placeholder="Minecraft, Fortnite, Roblox..."
)

# Récupérer les jeux gratuits Steam
@st.cache_data(ttl=600)
def jeux_gratuits_steam():
    url = (
        "https://store.steampowered.com/search/"
        "?category1=998&supportedlang=french"
    )

    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        jeux = []

        for item in soup.select("a.search_result_row"):
            titre = item.select_one(".title")
            image = item.select_one("img")

            if not titre:
                continue

            jeux.append({
                "nom": titre.get_text(strip=True),
                "image": image.get("src", "") if image else "",
                "lien": item.get("href", ""),
                "boutique": "Steam"
            })

        return jeux

    except Exception as e:
        st.error(f"Erreur Steam : {e}")
        return []

# Récupérer les jeux gratuits Epic Games
@st.cache_data(ttl=1800)
def jeux_gratuits_epic():
    url = (
        "https://store-site-backend-static.ak.epicgames.com/"
        "freeGamesPromotions?locale=fr-FR&country=FR"
    )

    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()

        data = r.json()
        elements = (
            data.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )

        jeux = []

        for item in elements:
            promotions = item.get("promotions") or {}
            offres = promotions.get("promotionalOffers", [])

            gratuit = any(
                offre.get("discountSetting", {}).get(
                    "discountPercentage"
                ) == 0
                for groupe in offres
                for offre in groupe.get("promotionalOffers", [])
            )

            if not gratuit:
                continue

            images = item.get("keyImages", [])
            image = images[0].get("url", "") if images else ""
            slug = item.get("productSlug") or item.get("urlSlug")

            lien = (
                "https://store.epicgames.com/fr/p/" + slug
                if slug else "https://store.epicgames.com/fr/free-games"
            )

            jeux.append({
                "nom": item.get("title", "Jeu gratuit"),
                "image": image,
                "lien": lien,
                "boutique": "Epic Games"
            })

        return jeux

    except Exception as e:
        st.error(f"Erreur Epic Games : {e}")
        return []

# Afficher les jeux
def afficher_jeux(jeux):
    if recherche:
        jeux = [
            jeu for jeu in jeux
            if recherche.lower() in jeu["nom"].lower()
        ]

    if not jeux:
        st.info("Aucun jeu trouvé dans cette catégorie.")
        return

    colonnes = st.columns(3)

    for i, jeu in enumerate(jeux):
        with colonnes[i % 3]:
            with st.container(border=True):
                if jeu["image"]:
                    st.image(jeu["image"], use_container_width=True)

                st.markdown("**" + jeu["nom"] + "**")
                st.caption(jeu["boutique"])

                st.link_button(
                    "🎮 Voir le jeu",
                    jeu["lien"],
                    use_container_width=True
                )

# PAGE D'ACCUEIL : JEUX GRATUITS
st.header("🆓 Jeux gratuits")

with st.spinner("Chargement des jeux gratuits..."):
    steam = jeux_gratuits_steam()
    epic = jeux_gratuits_epic()

gratuits = steam + epic

st.caption(f"{len(gratuits)} jeux récupérés")

afficher_jeux(gratuits)

# PROMOTIONS
st.divider()
st.header("🔥 Promotions Steam")

if st.button("Afficher les promotions"):
    st.link_button(
        "Voir toutes les promotions Steam",
        "https://store.steampowered.com/search/?specials=1"
    )

# NOUVEAUTÉS
st.divider()
st.header("✨ Nouveautés Steam")

if st.button("Afficher les nouveautés"):
    st.link_button(
        "Voir les nouveautés Steam",
        "https://store.steampowered.com/explore/new/"
    )

st.divider()
st.caption("GameDeals 🎮")
