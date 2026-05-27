from typing import List, Optional
from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.argos_scraper import ArgosScraper
from app.scrapers.currys_scraper import CurrysScraper
from app.scrapers.ebay_scraper import EbayScraper
from app.scrapers.john_lewis_scraper import JohnLewisScraper
from app.scrapers.additional_scrapers import AOScraper, VeryScraper, ScanScraper
from app.utils.price_normalizer import normalize_price
from app.utils.logger import logger

# ─────────────────────────────────────────────────────────────────────────────
# REGION CONFIG
# ─────────────────────────────────────────────────────────────────────────────
REGIONS = {
    "uk": {"name": "United Kingdom", "currency": "GBP", "symbol": "£"},
    "us": {"name": "United States",  "currency": "USD", "symbol": "$"},
    "in": {"name": "India",          "currency": "INR", "symbol": "₹"},
}

# ─────────────────────────────────────────────────────────────────────────────
# MOCK PRODUCT DATABASE — UK
# ─────────────────────────────────────────────────────────────────────────────
UK_PRODUCTS = {
    "iphone": [
        {"store": "Amazon UK",   "title": "Apple iPhone 15 Pro 128GB Natural Titanium",         "description": "6.1-inch Super Retina XDR, A17 Pro chip, 48MP camera, USB-C, titanium design.",              "price": 999.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=iphone+15+pro"},
        {"store": "Argos",       "title": "Apple iPhone 15 Pro 128GB Natural Titanium",         "description": "A17 Pro chip, ProMotion display, Action button, USB-C. SIM-free or on contract.",             "price": 1029.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/iphone-15-pro/"},
        {"store": "Currys",      "title": "APPLE iPhone 15 Pro 128GB Natural Titanium",         "description": "Pro camera system, A17 Pro, titanium frame, USB-C, 6.1-inch OLED.",                          "price": 1019.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=iphone+15+pro"},
        {"store": "eBay UK",     "title": "Apple iPhone 15 Pro 128GB Titanium Unlocked",        "description": "Brand new sealed, UK model, unlocked all networks, full Apple warranty.",                     "price": 949.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=iphone+15+pro"},
        {"store": "John Lewis",  "title": "Apple iPhone 15 Pro 128GB Natural Titanium",         "description": "2-year John Lewis guarantee. A17 Pro, 48MP, USB-C, Action button.",                          "price": 999.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=iphone+15+pro"},
        {"store": "Very",        "title": "Apple iPhone 15 Pro 128GB Titanium",                 "description": "Buy on credit. A17 Pro, titanium build, USB-C.",                                              "price": 1049.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=iphone+15+pro"},
        {"store": "AO",          "title": "Apple iPhone 15 Pro 128GB Natural Titanium",         "description": "Fast dispatch. Titanium design, A17 Pro chip, USB-C connector.",                             "price": 1009.00, "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://ao.com/search?q=iphone+15+pro"},
        {"store": "Scan",        "title": "Apple iPhone 15 Pro 128GB Titanium",                 "description": "SIM-free UK stock. A17 Pro, ProMotion OLED, 5G.",                                            "price": 979.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=iphone+15+pro"},
    ],
    "samsung": [
        {"store": "Amazon UK",   "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",      "description": "6.8-inch QHD+, Snapdragon 8 Gen 3, 200MP, built-in S Pen, 5000mAh.",                        "price": 1249.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=samsung+s24+ultra"},
        {"store": "Argos",       "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",      "description": "200MP camera, S Pen, Snapdragon 8 Gen 3, titanium finish.",                                  "price": 1299.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/samsung-s24-ultra/"},
        {"store": "Currys",      "title": "SAMSUNG Galaxy S24 Ultra 256GB Black",               "description": "AI-enhanced S24 Ultra, S Pen, 200MP quad camera, premium titanium.",                         "price": 1279.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=samsung+s24+ultra"},
        {"store": "eBay UK",     "title": "Samsung Galaxy S24 Ultra 256GB Black Unlocked",      "description": "New sealed, unlocked for all networks, 12 months warranty.",                                  "price": 1199.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=samsung+s24+ultra"},
        {"store": "John Lewis",  "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",      "description": "2-year guarantee. 200MP camera, S Pen, Snapdragon 8 Gen 3.",                                 "price": 1249.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=samsung+s24+ultra"},
        {"store": "Very",        "title": "Samsung Galaxy S24 Ultra 256GB Black",               "description": "Buy on credit. AI cameras, S Pen, 5G.",                                                      "price": 1319.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=samsung+s24+ultra"},
        {"store": "AO",          "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",      "description": "Next-day delivery. S Pen, 200MP, Snapdragon 8 Gen 3.",                                       "price": 1259.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=samsung+s24+ultra"},
        {"store": "Scan",        "title": "Samsung Galaxy S24 Ultra 256GB Black",               "description": "UK model. Galaxy AI, 200MP quad-camera.",                                                    "price": 1219.00, "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://www.scan.co.uk/search?q=samsung+s24+ultra"},
    ],
    "ps5": [
        {"store": "Amazon UK",   "title": "PlayStation 5 Slim Console Disc Edition",            "description": "1TB SSD, DualSense controller, 4K gaming, 120fps, backward compatible.",                     "price": 389.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=ps5+slim"},
        {"store": "Argos",       "title": "Sony PlayStation 5 Slim Console",                    "description": "Ultra-high-speed SSD, DualSense haptic feedback, 4K output.",                                "price": 389.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/ps5-slim/"},
        {"store": "Currys",      "title": "SONY PlayStation 5 Slim Console",                    "description": "1TB SSD, DualSense, 4K/120fps, backward compatible with PS4 titles.",                        "price": 399.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=ps5+slim"},
        {"store": "eBay UK",     "title": "Sony PS5 Slim Console Brand New Sealed",             "description": "Brand new sealed PS5 Slim, UK model, 12 months Sony warranty.",                              "price": 369.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=ps5+slim"},
        {"store": "John Lewis",  "title": "Sony PlayStation 5 Slim Disc Edition",               "description": "2-year guarantee. 1TB SSD, DualSense, 4K gaming.",                                           "price": 389.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=ps5+slim"},
        {"store": "Very",        "title": "PlayStation 5 Slim Console",                         "description": "Credit available. 1TB SSD, DualSense wireless controller.",                                  "price": 409.00,  "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=ps5+slim"},
        {"store": "AO",          "title": "Sony PlayStation 5 Slim",                            "description": "Next-day delivery. 1TB SSD, DualSense, 4K, backward compatible.",                            "price": 389.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=ps5+slim"},
        {"store": "Scan",        "title": "Sony PlayStation 5 Slim 1TB",                        "description": "In stock. Disc Edition, UK model, DualSense included.",                                      "price": 384.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=ps5+slim"},
    ],
    "macbook": [
        {"store": "Amazon UK",   "title": "Apple MacBook Air 13-inch M3 8GB 256GB Midnight",   "description": "M3 chip, 18-hour battery, 13.6-inch Liquid Retina, MagSafe, fanless.",                       "price": 1099.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=macbook+air+m3"},
        {"store": "Argos",       "title": "Apple MacBook Air 13 M3 8GB 256GB Midnight",        "description": "M3 chip, 18hr battery, Liquid Retina display, MagSafe 3.",                                   "price": 1149.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/macbook-air-m3/"},
        {"store": "Currys",      "title": "APPLE MacBook Air 13 M3 8GB 256GB Midnight",        "description": "Fanless design, Liquid Retina, M3 chip, MagSafe 3 charging.",                                "price": 1129.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=macbook+air+m3"},
        {"store": "eBay UK",     "title": "Apple MacBook Air M3 13 8GB 256GB Midnight 2024",   "description": "Brand new sealed, UK model, Liquid Retina, MagSafe.",                                        "price": 1049.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=macbook+air+m3"},
        {"store": "John Lewis",  "title": "Apple MacBook Air 13-inch M3 8GB 256GB Midnight",   "description": "2-year guarantee. M3, 18hr battery, Liquid Retina, MagSafe.",                                "price": 1099.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=macbook+air+m3"},
        {"store": "Very",        "title": "Apple MacBook Air 13 M3 Midnight",                  "description": "Credit available. M3 chip, Liquid Retina, all-day battery.",                                 "price": 1159.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=macbook+air+m3"},
        {"store": "AO",          "title": "Apple MacBook Air 13-inch M3 Midnight",              "description": "Fast dispatch. M3, fanless, 18hr battery, MagSafe.",                                         "price": 1109.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=macbook+air+m3"},
        {"store": "Scan",        "title": "Apple MacBook Air 13 M3 8GB 256GB",                 "description": "UK stock. M3 chip, Liquid Retina, 1.24 kg lightweight.",                                     "price": 1089.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=macbook+air+m3"},
    ],
    "dyson": [
        {"store": "Amazon UK",   "title": "Dyson V15 Detect Absolute Vacuum Cleaner",          "description": "Laser dust detection, HEPA filtration, 60-min runtime, acoustic piezo sensor.",              "price": 549.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=dyson+v15"},
        {"store": "Argos",       "title": "Dyson V15 Detect Absolute Cordless Vacuum",         "description": "Laser reveal, piezo sensor, 60 min battery, full-size suction.",                             "price": 579.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/dyson-v15/"},
        {"store": "Currys",      "title": "DYSON V15 Detect Absolute Cordless Vacuum",         "description": "Laser-guided, 60 min runtime, HEPA whole-machine filtration.",                               "price": 569.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=dyson+v15"},
        {"store": "eBay UK",     "title": "Dyson V15 Detect Absolute Brand New",               "description": "New sealed, UK model, full manufacturer warranty.",                                           "price": 499.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=dyson+v15"},
        {"store": "John Lewis",  "title": "Dyson V15 Detect Absolute",                         "description": "2-year guarantee. Detects and counts particles, 60min runtime.",                              "price": 549.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=dyson+v15"},
        {"store": "AO",          "title": "Dyson V15 Detect Absolute",                         "description": "Next-day. Piezo sensor, laser reveal, 60 min runtime.",                                      "price": 554.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=dyson+v15"},
        {"store": "Very",        "title": "Dyson V15 Detect Absolute Cordless Vacuum",         "description": "On credit. Laser detection, HEPA filter, 60 min battery.",                                   "price": 589.00,  "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=dyson+v15"},
        {"store": "Scan",        "title": "Dyson V15 Detect Absolute Vacuum",                  "description": "In stock. Cordless, laser dust detection, HEPA filtration.",                                 "price": 539.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=dyson+v15"},
    ],
    "airpods": [
        {"store": "Amazon UK",   "title": "Apple AirPods Pro 2nd Gen MagSafe USB-C",           "description": "ANC, Adaptive Audio, H2 chip, 6hr + 30hr with case, IPX4.",                                 "price": 229.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=airpods+pro+2"},
        {"store": "Argos",       "title": "Apple AirPods Pro 2nd Gen MagSafe Case",            "description": "H2 chip, ANC, Adaptive Transparency, Personalised Spatial Audio.",                           "price": 249.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/airpods-pro-2/"},
        {"store": "Currys",      "title": "APPLE AirPods Pro 2nd Gen Wireless Earbuds",        "description": "Improved ANC, Adaptive Audio, USB-C MagSafe, 30hr total.",                                   "price": 239.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=airpods+pro+2"},
        {"store": "eBay UK",     "title": "Apple AirPods Pro 2nd Gen MagSafe Sealed",          "description": "New sealed, USB-C, UK stock, full Apple warranty.",                                          "price": 209.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=airpods+pro+2"},
        {"store": "John Lewis",  "title": "Apple AirPods Pro 2nd Generation",                  "description": "2-year guarantee. ANC, H2 chip, MagSafe USB-C.",                                            "price": 229.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=airpods+pro+2"},
        {"store": "Scan",        "title": "Apple AirPods Pro 2nd Gen USB-C",                   "description": "In stock. ANC, Personalised Spatial Audio, 6hr per charge.",                                "price": 219.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=airpods+pro+2"},
        {"store": "Very",        "title": "Apple AirPods Pro 2nd Gen",                         "description": "Credit available. ANC, 30hr total battery, MagSafe.",                                        "price": 259.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=airpods+pro+2"},
        {"store": "AO",          "title": "Apple AirPods Pro 2nd Generation",                  "description": "Fast dispatch. H2 chip, ANC, Adaptive Audio, USB-C MagSafe.",                               "price": 234.00,  "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://ao.com/search?q=airpods+pro+2"},
    ],
    "tv": [
        {"store": "Amazon UK",   "title": "LG OLED55C34LA 55\" OLED 4K Smart TV",              "description": "OLED evo panel, a9 AI Gen6, Dolby Vision IQ, 120Hz, HDMI 2.1, webOS 23.",                   "price": 1099.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=lg+oled+55+c3"},
        {"store": "Currys",      "title": "LG OLED55C34LA 55 Smart 4K OLED TV",               "description": "OLED evo, Dolby Vision IQ, G-Sync, FreeSync, 4x HDMI 2.1.",                                 "price": 1149.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=lg+oled55c3"},
        {"store": "John Lewis",  "title": "LG OLED55C34LA 55\" 4K OLED Smart TV",              "description": "5-year guarantee. OLED evo, a9 Gen 6 AI, Dolby Vision, 120Hz.",                             "price": 1099.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=lg+oled+55+c3"},
        {"store": "Argos",       "title": "LG 55\" OLED C3 4K Ultra HD HDR Smart TV",          "description": "Perfect blacks, OLED evo, a9 AI, Dolby Vision, 120Hz.",                                     "price": 1199.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/lg-oled-55-c3/"},
        {"store": "eBay UK",     "title": "LG 55 C3 OLED 4K Smart TV 2023 Ex Display",        "description": "Ex-display, near-perfect condition, all accessories included.",                               "price": 899.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=lg+oled+55+c3"},
        {"store": "AO",          "title": "LG OLED55C34LA 55\" OLED C3 4K TV",                "description": "Next-day delivery. OLED evo, 4K, 120Hz, webOS.",                                             "price": 1079.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=lg+oled55c3"},
        {"store": "Very",        "title": "LG 55C3 OLED 4K Smart TV",                         "description": "Credit available. OLED, 4K, 120Hz, Dolby Atmos.",                                            "price": 1249.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=lg+oled+55+c3"},
        {"store": "Scan",        "title": "LG OLED 55C3 4K TV 2023",                          "description": "In stock. OLED evo, 120Hz, G-Sync, 4x HDMI 2.1.",                                           "price": 1049.00, "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=lg+oled55c3"},
    ],
    "laptop": [
        {"store": "Amazon UK",   "title": "Lenovo IdeaPad 5 15.6\" Core i5 16GB 512GB",       "description": "15.6-inch FHD IPS, Intel i5-1235U, 16GB RAM, 512GB NVMe, Windows 11.",                     "price": 649.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=lenovo+ideapad+5+i5"},
        {"store": "Currys",      "title": "DELL Inspiron 15 Core i5 16GB 512GB SSD",          "description": "15.6-inch FHD, Intel Core i5, 16GB, 512GB SSD, Windows 11.",                               "price": 699.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=dell+inspiron+15+i5"},
        {"store": "John Lewis",  "title": "ASUS VivoBook 15 Core i5 16GB 512GB",              "description": "2-year guarantee. ASUS VivoBook, i5, 16GB, 512GB, OLED FHD.",                               "price": 629.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=asus+vivobook+15"},
        {"store": "Argos",       "title": "HP 15s 15.6\" Core i5 8GB 256GB SSD",              "description": "15.6-inch FHD, Intel i5, 8GB DDR4, 256GB SSD, HP Fast Charge.",                            "price": 549.99,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/hp-15s-laptop/"},
        {"store": "eBay UK",     "title": "Lenovo ThinkPad E15 i5 16GB 512GB Refurbished",    "description": "Refurbished Grade A, Core i5, 16GB, 512GB. Full working order.",                           "price": 499.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=lenovo+thinkpad+e15+i5"},
        {"store": "Scan",        "title": "Dell Inspiron 15 AMD Ryzen 5 16GB 512GB",          "description": "AMD Ryzen 5, 16GB, 512GB NVMe, 15.6 FHD.",                                                 "price": 579.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=dell+inspiron+15+laptop"},
        {"store": "Very",        "title": "HP Pavilion 15 Core i5 16GB 512GB",                "description": "Credit available. 15.6-inch FHD, Intel i5, 16GB, 512GB.",                                   "price": 659.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=hp+pavilion+15+i5"},
        {"store": "AO",          "title": "Lenovo IdeaPad 3 15.6\" Core i5 16GB 512GB",      "description": "Same-day dispatch. 15.6 FHD IPS, i5, 16GB, 512GB NVMe.",                                   "price": 619.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=lenovo+ideapad+i5+laptop"},
    ],
    "watch": [
        {"store": "Amazon UK",   "title": "Apple Watch Series 9 GPS 41mm Midnight Aluminium",  "description": "S9 chip, double-tap, 18hr battery, always-on Retina, ECG, crash detection.",               "price": 379.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=apple+watch+series+9"},
        {"store": "Currys",      "title": "APPLE Watch Series 9 GPS 41mm Midnight",            "description": "S9 chip, double tap, 18hr battery, always-on Retina.",                                      "price": 389.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=apple+watch+series+9"},
        {"store": "John Lewis",  "title": "Apple Watch Series 9 GPS 41mm Midnight",            "description": "2-year guarantee. S9, double tap, ECG, 18hr battery.",                                      "price": 379.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=apple+watch+series+9"},
        {"store": "Argos",       "title": "Apple Watch Series 9 GPS 41mm Midnight",            "description": "S9, always-on display, double tap, health sensors.",                                         "price": 399.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/apple-watch-series-9/"},
        {"store": "eBay UK",     "title": "Apple Watch Series 9 GPS 41mm Midnight Sealed",    "description": "Brand new sealed, UK model, full Apple warranty.",                                           "price": 349.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=apple+watch+series+9"},
        {"store": "Very",        "title": "Apple Watch Series 9 GPS 41mm",                    "description": "Credit available. S9, double tap, always-on, health sensors.",                               "price": 409.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=apple+watch+series+9"},
        {"store": "Scan",        "title": "Apple Watch Series 9 GPS 41mm Aluminium",          "description": "In stock. S9, double-tap, always-on Retina, crash detection.",                              "price": 369.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=apple+watch+series+9"},
        {"store": "AO",          "title": "Apple Watch Series 9 GPS 41mm Midnight",           "description": "Fast delivery. S9, double tap, ECG, 18hr battery.",                                         "price": 384.00,  "currency": "GBP", "in_stock": False, "region": "uk", "url": "https://ao.com/search?q=apple+watch+series+9"},
    ],
    "headphones": [
        {"store": "Amazon UK",   "title": "Sony WH-1000XM5 Wireless Noise Cancelling",        "description": "Industry-leading ANC, 30hr battery, multipoint, LDAC Hi-Res audio.",                       "price": 279.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.amazon.co.uk/s?k=sony+wh-1000xm5"},
        {"store": "Currys",      "title": "SONY WH-1000XM5 Wireless Headphones Black",        "description": "Dual noise sensor, 30hr battery, multipoint, Hi-Res Audio Wireless.",                       "price": 289.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.currys.co.uk/search?q=sony+wh-1000xm5"},
        {"store": "John Lewis",  "title": "Sony WH-1000XM5 Wireless Headphones",              "description": "2-year guarantee. Best ANC, 30hr battery, multipoint.",                                     "price": 279.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.johnlewis.com/search?search-term=sony+wh-1000xm5"},
        {"store": "Argos",       "title": "Sony WH-1000XM5 Noise Cancelling Headphones",      "description": "30hr ANC, 8 mics, speak-to-chat, multipoint Bluetooth.",                                   "price": 299.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.argos.co.uk/search/sony-wh-1000xm5/"},
        {"store": "eBay UK",     "title": "Sony WH-1000XM5 Headphones Brand New",             "description": "New sealed, UK model, full warranty.",                                                       "price": 259.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.ebay.co.uk/sch/i.html?_nkw=sony+wh+1000xm5"},
        {"store": "Scan",        "title": "Sony WH-1000XM5 Headphones Black",                 "description": "In stock. Best ANC, LDAC wireless audio.",                                                  "price": 269.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.scan.co.uk/search?q=sony+wh1000xm5"},
        {"store": "Very",        "title": "Sony WH-1000XM5 Headphones",                       "description": "On credit. 30hr ANC, Hi-Res Audio.",                                                        "price": 309.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://www.very.co.uk/search/results.aspx?sq=sony+wh-1000xm5"},
        {"store": "AO",          "title": "Sony WH-1000XM5 Wireless Headphones",              "description": "Fast delivery. Industry-leading ANC, 30hr battery.",                                        "price": 284.00,  "currency": "GBP", "in_stock": True,  "region": "uk", "url": "https://ao.com/search?q=sony+wh-1000xm5"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# MOCK PRODUCT DATABASE — US
# ─────────────────────────────────────────────────────────────────────────────
US_PRODUCTS = {
    "iphone": [
        {"store": "Amazon US",  "title": "Apple iPhone 15 Pro 128GB Natural Titanium",          "description": "6.1-inch Super Retina XDR, A17 Pro chip, 48MP camera, USB-C, titanium.",                    "price": 999.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=iphone+15+pro"},
        {"store": "Best Buy",   "title": "Apple iPhone 15 Pro 128GB Natural Titanium",          "description": "A17 Pro, ProMotion OLED, 48MP camera system, USB-C, Action button.",                        "price": 999.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=iphone+15+pro"},
        {"store": "Walmart",    "title": "Apple iPhone 15 Pro 128GB Titanium Unlocked",         "description": "Unlocked, works with any carrier. A17 Pro, 48MP, titanium frame.",                          "price": 989.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=iphone+15+pro"},
        {"store": "Target",     "title": "Apple iPhone 15 Pro 128GB Natural Titanium",          "description": "Available with carrier deals. A17 Pro chip, 48MP ProCamera system.",                        "price": 999.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=iphone+15+pro"},
        {"store": "eBay US",    "title": "Apple iPhone 15 Pro 128GB Titanium Unlocked New",     "description": "Brand new sealed, unlocked US model, full Apple warranty.",                                  "price": 949.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=iphone+15+pro"},
        {"store": "B&H Photo",  "title": "Apple iPhone 15 Pro 128GB Natural Titanium",          "description": "Factory unlocked, US model. A17 Pro, USB-C, 48MP ProCamera.",                              "price": 999.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=iphone+15+pro"},
        {"store": "Costco",     "title": "Apple iPhone 15 Pro 128GB Titanium Bundle",           "description": "Costco value bundle with accessories. A17 Pro, titanium, USB-C.",                          "price": 979.99,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=iphone+15+pro"},
        {"store": "Newegg",     "title": "Apple iPhone 15 Pro 128GB Natural Titanium",          "description": "SIM-free, US unlocked. A17 Pro Pro, ProMotion 120Hz, 48MP.",                               "price": 969.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.newegg.com/p/pl?d=iphone+15+pro"},
    ],
    "samsung": [
        {"store": "Amazon US",  "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",       "description": "6.8-inch QHD+, Snapdragon 8 Gen 3, 200MP, S Pen, 5000mAh.",                               "price": 1299.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=samsung+s24+ultra"},
        {"store": "Best Buy",   "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",       "description": "200MP camera, integrated S Pen, Snapdragon 8 Gen 3, 6.8-inch QHD+.",                       "price": 1299.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=samsung+s24+ultra"},
        {"store": "Walmart",    "title": "Samsung Galaxy S24 Ultra 256GB Black",                "description": "S Pen, 200MP camera, AI features, titanium frame, 5G.",                                    "price": 1279.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=samsung+s24+ultra"},
        {"store": "Target",     "title": "Samsung Galaxy S24 Ultra 256GB Titanium",             "description": "200MP ProVisual Engine, Galaxy AI, S Pen, Snapdragon 8 Gen 3.",                            "price": 1299.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=samsung+s24+ultra"},
        {"store": "eBay US",    "title": "Samsung Galaxy S24 Ultra 256GB Black Unlocked",       "description": "New sealed, US unlocked, 200MP, S Pen, full warranty.",                                    "price": 1199.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=samsung+s24+ultra"},
        {"store": "B&H Photo",  "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",       "description": "Unlocked US model. 200MP camera, S Pen, Snapdragon 8 Gen 3.",                              "price": 1249.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=samsung+s24+ultra"},
        {"store": "Costco",     "title": "Samsung Galaxy S24 Ultra 256GB Bundle",               "description": "Bundle with Samsung accessories. 200MP, S Pen, AI features.",                              "price": 1259.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=samsung+s24+ultra"},
        {"store": "Newegg",     "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",       "description": "US unlocked model. Galaxy AI, 200MP ProVisual Engine, S Pen.",                             "price": 1229.00, "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.newegg.com/p/pl?d=samsung+s24+ultra"},
    ],
    "ps5": [
        {"store": "Amazon US",  "title": "PlayStation 5 Slim Console Disc Edition",             "description": "1TB SSD, DualSense controller, 4K gaming, 120fps, backward compatible.",                   "price": 499.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=ps5+slim"},
        {"store": "Best Buy",   "title": "Sony PlayStation 5 Slim Console",                     "description": "Ultra-high-speed SSD, DualSense haptic, 4K output, backward compatible.",                  "price": 499.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=ps5+slim"},
        {"store": "Walmart",    "title": "PlayStation 5 Slim 1TB Console Disc Edition",         "description": "DualSense, 4K, 120fps, 1TB SSD, HDR. Backward compatible.",                               "price": 499.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=ps5+slim"},
        {"store": "Target",     "title": "Sony PlayStation 5 Slim Disc Console",                "description": "PS5 Slim with 1TB SSD, DualSense, 4K gaming, backward compatible.",                       "price": 499.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=ps5+slim"},
        {"store": "eBay US",    "title": "Sony PS5 Slim Console Brand New Sealed",              "description": "Brand new sealed, US model, 12 months warranty. Disc Edition.",                            "price": 469.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=ps5+slim"},
        {"store": "Newegg",     "title": "Sony PlayStation 5 Slim 1TB Disc Edition",            "description": "In stock. 1TB SSD, DualSense, 4K/120fps, backward compatible.",                            "price": 499.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.newegg.com/p/pl?d=ps5+slim"},
        {"store": "Costco",     "title": "PlayStation 5 Slim Console Bundle",                   "description": "Bundle with extra controller and game. 1TB SSD, 4K, 120fps.",                             "price": 549.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=ps5+slim"},
        {"store": "B&H Photo",  "title": "Sony PlayStation 5 Slim Console Disc Edition",        "description": "US model. DualSense haptic feedback, 1TB SSD, 4K gaming.",                                "price": 499.99,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=ps5+slim"},
    ],
    "macbook": [
        {"store": "Amazon US",  "title": "Apple MacBook Air 13-inch M3 8GB 256GB Midnight",    "description": "M3 chip, 18hr battery, 13.6-inch Liquid Retina, MagSafe, fanless.",                        "price": 1099.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=macbook+air+m3"},
        {"store": "Best Buy",   "title": "Apple MacBook Air 13\" M3 8GB 256GB Midnight",       "description": "M3 chip, Liquid Retina, MagSafe 3, 18hr battery, 1.24 kg.",                               "price": 1099.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=macbook+air+m3"},
        {"store": "Walmart",    "title": "Apple MacBook Air 13-inch M3 Midnight",               "description": "M3 processor, fanless design, 18-hour battery, Liquid Retina.",                           "price": 1089.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=macbook+air+m3"},
        {"store": "Target",     "title": "Apple MacBook Air 13\" M3 8GB 256GB Midnight",       "description": "Up to 18hr battery, M3 chip, Liquid Retina display, MagSafe.",                            "price": 1099.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=macbook+air+m3"},
        {"store": "B&H Photo",  "title": "Apple MacBook Air 13\" M3 Chip 8GB 256GB Midnight",  "description": "Factory fresh, US model. M3, Liquid Retina, MagSafe, fanless.",                            "price": 1099.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=macbook+air+m3"},
        {"store": "Costco",     "title": "Apple MacBook Air M3 Bundle",                         "description": "Bundle with AppleCare. M3, 8GB, 256GB, 18hr battery.",                                    "price": 1149.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=macbook+air+m3"},
        {"store": "eBay US",    "title": "Apple MacBook Air M3 13 8GB 256GB Midnight 2024",    "description": "New sealed US model. M3, Liquid Retina, MagSafe 3.",                                       "price": 1049.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=macbook+air+m3"},
        {"store": "Newegg",     "title": "Apple MacBook Air 13-inch M3 8GB 256GB",             "description": "US stock. M3, fanless, 1.24 kg, 18hr battery, Liquid Retina.",                            "price": 1079.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.newegg.com/p/pl?d=macbook+air+m3"},
    ],
    "airpods": [
        {"store": "Amazon US",  "title": "Apple AirPods Pro 2nd Gen USB-C MagSafe",            "description": "ANC, Adaptive Audio, H2 chip, 6hr + 30hr case, IPX4 water resistant.",                    "price": 249.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=airpods+pro+2"},
        {"store": "Best Buy",   "title": "Apple AirPods Pro 2nd Generation USB-C",             "description": "Active Noise Cancellation, Adaptive Audio, Personalised Spatial Audio.",                   "price": 249.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=airpods+pro+2"},
        {"store": "Walmart",    "title": "Apple AirPods Pro 2nd Gen MagSafe",                  "description": "ANC, USB-C, 30hr total battery, Adaptive Audio.",                                         "price": 239.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=airpods+pro+2"},
        {"store": "Target",     "title": "Apple AirPods Pro 2nd Generation",                   "description": "H2 chip, ANC, Adaptive Transparency, MagSafe USB-C case.",                                "price": 249.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=airpods+pro+2"},
        {"store": "B&H Photo",  "title": "Apple AirPods Pro 2nd Gen USB-C MagSafe",            "description": "US model. ANC, H2 chip, Adaptive Audio, 30hr total battery.",                             "price": 249.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=airpods+pro+2"},
        {"store": "Costco",     "title": "Apple AirPods Pro 2nd Gen Bundle",                   "description": "With extra ear tips. ANC, Adaptive Audio, USB-C MagSafe.",                                "price": 229.99,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=airpods+pro+2"},
        {"store": "eBay US",    "title": "Apple AirPods Pro 2nd Gen USB-C Sealed",             "description": "New sealed US model. ANC, H2, Adaptive Audio.",                                           "price": 219.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=airpods+pro+2"},
        {"store": "Newegg",     "title": "Apple AirPods Pro 2nd Generation USB-C",             "description": "In stock. ANC, Personalised Spatial Audio, 6hr per charge.",                              "price": 239.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.newegg.com/p/pl?d=airpods+pro+2"},
    ],
    "tv": [
        {"store": "Amazon US",  "title": "LG OLED55C3PUA 55\" OLED 4K Smart TV 2023",          "description": "OLED evo, a9 AI Gen6, Dolby Vision IQ, 120Hz, HDMI 2.1, webOS 23.",                      "price": 1296.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=lg+oled+55+c3"},
        {"store": "Best Buy",   "title": "LG 55\" Class C3 Series OLED 4K Smart TV",           "description": "OLED evo panel, a9 AI Processor Gen6, NVIDIA G-Sync, FreeSync.",                         "price": 1299.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=lg+oled+55+c3"},
        {"store": "Walmart",    "title": "LG 55\" OLED C3 4K Smart TV",                        "description": "OLED evo, 4K, 120Hz, Dolby Vision, HDMI 2.1, webOS.",                                    "price": 1267.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=lg+oled+55+c3"},
        {"store": "Target",     "title": "LG 55\" 4K OLED Smart TV C3",                        "description": "OLED evo, a9 AI, perfect blacks, 120Hz, Dolby Vision IQ.",                               "price": 1299.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=lg+oled+55+c3"},
        {"store": "B&H Photo",  "title": "LG 55\" C3 OLED 4K HDR Smart TV",                   "description": "OLED evo panel, a9 Gen 6, Dolby Vision, 4x HDMI 2.1.",                                   "price": 1296.95, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=lg+oled+55+c3"},
        {"store": "Costco",     "title": "LG 55\" C3 OLED 4K Smart TV with Warranty",          "description": "With extended warranty. OLED evo, 120Hz, webOS, Dolby Vision.",                          "price": 1249.99, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=lg+oled+55+c3"},
        {"store": "eBay US",    "title": "LG OLED55C3 55\" C3 4K OLED TV New",                 "description": "New US model. OLED evo, 120Hz, Dolby Vision IQ, webOS 23.",                               "price": 1149.00, "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=lg+oled+55+c3"},
        {"store": "Newegg",     "title": "LG OLED55C3PUA 55\" 4K OLED TV",                    "description": "OLED evo, a9 AI Gen 6, 120Hz, HDMI 2.1, Dolby Vision IQ.",                               "price": 1279.00, "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.newegg.com/p/pl?d=lg+oled+55+c3"},
    ],
    "laptop": [
        {"store": "Amazon US",  "title": "Lenovo IdeaPad 5 15.6\" Intel Core i5 16GB 512GB",  "description": "15.6-inch FHD IPS, Intel i5-1235U, 16GB RAM, 512GB NVMe, Windows 11.",                   "price": 649.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=lenovo+ideapad+5+i5"},
        {"store": "Best Buy",   "title": "Dell Inspiron 15 15.6\" Laptop i5 16GB 512GB",      "description": "15.6-inch FHD, Intel Core i5, 16GB, 512GB SSD, Windows 11 Home.",                       "price": 699.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=dell+inspiron+15+i5"},
        {"store": "Walmart",    "title": "HP 15.6\" Laptop Intel Core i5 8GB 256GB",          "description": "15.6-inch FHD, Intel i5, 8GB DDR4, 256GB SSD, HP Fast Charge.",                          "price": 549.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=hp+laptop+i5"},
        {"store": "Target",     "title": "ASUS VivoBook 15.6\" Core i5 16GB 512GB",           "description": "OLED FHD, Intel i5, 16GB, 512GB SSD, Windows 11.",                                       "price": 629.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=asus+vivobook+i5"},
        {"store": "B&H Photo",  "title": "Lenovo ThinkPad E15 Gen 4 15.6\" i5 16GB 512GB",   "description": "Business laptop, MIL-SPEC tested, i5, 16GB, 512GB SSD.",                                 "price": 729.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=lenovo+thinkpad+e15+i5"},
        {"store": "Costco",     "title": "HP Envy 15.6\" Laptop i5 16GB 512GB Bundle",        "description": "Bundle with Office. 15.6-inch FHD, Intel i5, 16GB, 512GB.",                              "price": 679.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=hp+envy+laptop+i5"},
        {"store": "eBay US",    "title": "Lenovo ThinkPad T14 i5 16GB 512GB Refurbished",     "description": "Grade A refurbished, Core i5, 16GB, 512GB SSD. Works perfectly.",                        "price": 499.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=lenovo+thinkpad+i5"},
        {"store": "Newegg",     "title": "MSI Modern 15 Core i5 16GB 512GB Laptop",           "description": "15.6-inch IPS FHD, Intel Core i5, 16GB, 512GB NVMe.",                                   "price": 599.00,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.newegg.com/p/pl?d=msi+modern+15+i5"},
    ],
    "headphones": [
        {"store": "Amazon US",  "title": "Sony WH-1000XM5 Wireless Noise Cancelling",         "description": "Industry-leading ANC, 30hr battery, multipoint, LDAC Hi-Res audio.",                      "price": 279.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=sony+wh-1000xm5"},
        {"store": "Best Buy",   "title": "Sony WH1000XM5 Noise Cancelling Headphones",        "description": "Best-in-class ANC, 30hr battery, multipoint Bluetooth, speak-to-chat.",                  "price": 279.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=sony+wh-1000xm5"},
        {"store": "Walmart",    "title": "Sony WH-1000XM5 Wireless Headphones Black",         "description": "30hr ANC, multipoint pairing, LDAC, USB-C, Bluetooth 5.2.",                             "price": 269.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=sony+wh-1000xm5"},
        {"store": "Target",     "title": "Sony WH-1000XM5 Wireless Headphones",               "description": "Best-in-class ANC, 8 mics, 30hr battery, Hi-Res Audio.",                                 "price": 279.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=sony+wh-1000xm5"},
        {"store": "B&H Photo",  "title": "Sony WH-1000XM5 Wireless NC Headphones",           "description": "US model. LDAC, industry-leading ANC, 30hr, multipoint.",                                "price": 279.95,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=sony+wh-1000xm5"},
        {"store": "Costco",     "title": "Sony WH-1000XM5 Headphones Bundle",                 "description": "With carry case bundle. 30hr ANC, LDAC, multipoint.",                                    "price": 259.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=sony+wh-1000xm5"},
        {"store": "eBay US",    "title": "Sony WH-1000XM5 Headphones Brand New",              "description": "New sealed US model. Best ANC, 30hr battery.",                                            "price": 249.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=sony+wh+1000xm5"},
        {"store": "Newegg",     "title": "Sony WH-1000XM5 Over-Ear Headphones Black",         "description": "In stock. Industry-leading ANC, LDAC, 30hr battery.",                                    "price": 269.00,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.newegg.com/p/pl?d=sony+wh-1000xm5"},
    ],
    "watch": [
        {"store": "Amazon US",  "title": "Apple Watch Series 9 GPS 41mm Midnight Aluminium",  "description": "S9 chip, double-tap, 18hr battery, always-on Retina, ECG, crash detection.",             "price": 329.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.amazon.com/s?k=apple+watch+series+9"},
        {"store": "Best Buy",   "title": "Apple Watch Series 9 GPS 41mm Midnight",            "description": "S9 SiP, double tap, always-on Retina, 18hr battery, ECG.",                               "price": 329.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bestbuy.com/site/searchpage.jsp?st=apple+watch+series+9"},
        {"store": "Walmart",    "title": "Apple Watch Series 9 GPS 41mm Midnight",            "description": "S9 chip, double tap gesture, crash detection, ECG, blood oxygen.",                       "price": 319.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.walmart.com/search?q=apple+watch+series+9"},
        {"store": "Target",     "title": "Apple Watch Series 9 GPS 41mm",                    "description": "S9 chip, double tap, always-on, health sensors, 18hr battery.",                          "price": 329.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.target.com/s?searchTerm=apple+watch+series+9"},
        {"store": "B&H Photo",  "title": "Apple Watch Series 9 GPS 41mm Midnight Aluminium", "description": "US model. S9, double-tap, always-on Retina, crash detection.",                           "price": 329.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.bhphotovideo.com/c/search?q=apple+watch+series+9"},
        {"store": "Costco",     "title": "Apple Watch Series 9 GPS Bundle",                  "description": "With extra band. S9, double tap, ECG, always-on Retina.",                                "price": 309.99,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.costco.com/catalogsearch/results?q=apple+watch+series+9"},
        {"store": "eBay US",    "title": "Apple Watch Series 9 GPS 41mm Midnight Sealed",    "description": "Brand new US model. S9 chip, double tap, always-on.",                                    "price": 299.00,  "currency": "USD", "in_stock": True,  "region": "us", "url": "https://www.ebay.com/sch/i.html?_nkw=apple+watch+series+9"},
        {"store": "Newegg",     "title": "Apple Watch Series 9 GPS 41mm Aluminium",           "description": "US stock. S9, double-tap, always-on Retina, IPX6 rated.",                                "price": 319.00,  "currency": "USD", "in_stock": False, "region": "us", "url": "https://www.newegg.com/p/pl?d=apple+watch+series+9"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# MOCK PRODUCT DATABASE — INDIA
# ─────────────────────────────────────────────────────────────────────────────
IN_PRODUCTS = {
    "iphone": [
        {"store": "Amazon IN",        "title": "Apple iPhone 15 Pro 128GB Natural Titanium",     "description": "6.1-inch Super Retina XDR, A17 Pro, 48MP camera, USB-C, titanium design.",              "price": 134900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=iphone+15+pro"},
        {"store": "Flipkart",         "title": "Apple iPhone 15 Pro 128GB Natural Titanium",     "description": "A17 Pro chip, ProMotion OLED, 48MP ProCamera, USB-C, Action button.",                   "price": 133900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=iphone+15+pro"},
        {"store": "Croma",            "title": "Apple iPhone 15 Pro 128GB Titanium",             "description": "A17 Pro, Super Retina XDR, 48MP ProCamera, USB-C. Available in stores.",                "price": 134900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=iphone+15+pro"},
        {"store": "Reliance Digital", "title": "Apple iPhone 15 Pro 128GB Natural Titanium",     "description": "Titanium design, A17 Pro, 48MP camera, USB-C connector.",                               "price": 134900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=iphone+15+pro"},
        {"store": "Tata CLiQ",        "title": "Apple iPhone 15 Pro 128GB Titanium",             "description": "A17 Pro chip, ProMotion OLED display, 48MP camera system, USB-C.",                      "price": 132999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=iphone+15+pro"},
        {"store": "Vijay Sales",      "title": "Apple iPhone 15 Pro 128GB Natural Titanium",     "description": "A17 Pro, 6.1-inch Super Retina XDR, 48MP, USB-C. EMI available.",                      "price": 134900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/iphone-15-pro"},
        {"store": "eBay IN",          "title": "Apple iPhone 15 Pro 128GB Titanium Unlocked",    "description": "Sealed, Indian variant, full warranty. A17 Pro, USB-C.",                                "price": 129999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=iphone+15+pro"},
        {"store": "Snapdeal",         "title": "Apple iPhone 15 Pro 128GB",                      "description": "A17 Pro chip, 48MP ProCamera, titanium design, USB-C. Ships from India.",               "price": 131990.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.snapdeal.com/search?keyword=iphone+15+pro"},
    ],
    "samsung": [
        {"store": "Amazon IN",        "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",  "description": "6.8-inch QHD+, Snapdragon 8 Gen 3, 200MP, S Pen, 5000mAh battery.",                    "price": 129999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=samsung+s24+ultra"},
        {"store": "Flipkart",         "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",  "description": "200MP camera, S Pen, Snapdragon 8 Gen 3, Galaxy AI features.",                         "price": 127999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=samsung+s24+ultra"},
        {"store": "Croma",            "title": "Samsung Galaxy S24 Ultra 256GB Black",           "description": "Galaxy AI, S Pen, 200MP ProVisual Engine. Available in-store and online.",             "price": 129999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=samsung+s24+ultra"},
        {"store": "Reliance Digital", "title": "Samsung Galaxy S24 Ultra 256GB",                 "description": "AI-powered S24 Ultra, S Pen, 200MP quad camera, titanium finish.",                     "price": 129999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=samsung+s24+ultra"},
        {"store": "Tata CLiQ",        "title": "Samsung Galaxy S24 Ultra 256GB Titanium Black",  "description": "200MP, S Pen, Snapdragon 8 Gen 3. Available on easy EMI.",                            "price": 126999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=samsung+s24+ultra"},
        {"store": "Vijay Sales",      "title": "Samsung Galaxy S24 Ultra 256GB Black",           "description": "Snapdragon 8 Gen 3, S Pen, 200MP. No-cost EMI available.",                             "price": 129999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/samsung-s24-ultra"},
        {"store": "eBay IN",          "title": "Samsung Galaxy S24 Ultra 256GB Unlocked",        "description": "Sealed Indian model. 200MP, S Pen, Galaxy AI.",                                        "price": 122999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=samsung+s24+ultra"},
        {"store": "Snapdeal",         "title": "Samsung Galaxy S24 Ultra 256GB Black",           "description": "Galaxy AI, S Pen, 200MP ProVisual Engine. Fast shipping.",                             "price": 124999.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.snapdeal.com/search?keyword=samsung+s24+ultra"},
    ],
    "ps5": [
        {"store": "Amazon IN",        "title": "Sony PlayStation 5 Slim Disc Edition",           "description": "1TB SSD, DualSense controller, 4K gaming, 120fps, backward compatible.",               "price": 54990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=ps5+slim"},
        {"store": "Flipkart",         "title": "Sony PlayStation 5 Slim Console",                "description": "Ultra-high-speed SSD, DualSense haptic feedback, 4K, backward compatible.",            "price": 54990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=ps5+slim"},
        {"store": "Croma",            "title": "Sony PlayStation 5 Slim Disc",                   "description": "1TB SSD, DualSense, 4K/120fps, haptic feedback. In-store collection available.",       "price": 54990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=ps5+slim"},
        {"store": "Reliance Digital", "title": "Sony PlayStation 5 Slim Console",                "description": "PS5 Slim with DualSense, 1TB SSD, 4K, backward compatible.",                          "price": 54990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=ps5+slim"},
        {"store": "Tata CLiQ",        "title": "Sony PlayStation 5 Slim Disc Edition",           "description": "1TB SSD, DualSense controller, 4K gaming. EMI available.",                            "price": 53999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=ps5+slim"},
        {"store": "Vijay Sales",      "title": "Sony PlayStation 5 Slim Console",                "description": "1TB SSD, DualSense haptic, 4K, 120fps. No-cost EMI.",                                 "price": 54990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/ps5-slim"},
        {"store": "eBay IN",          "title": "Sony PS5 Slim Console Brand New Sealed",         "description": "Brand new sealed Indian model. 1TB SSD, DualSense.",                                   "price": 52000.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=ps5+slim"},
        {"store": "Snapdeal",         "title": "Sony PlayStation 5 Slim Disc Edition",           "description": "1TB, DualSense controller, 4K gaming, backward compatible.",                           "price": 53490.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.snapdeal.com/search?keyword=ps5+slim"},
    ],
    "macbook": [
        {"store": "Amazon IN",        "title": "Apple MacBook Air 13-inch M3 8GB 256GB Midnight","description": "M3 chip, 18hr battery, 13.6-inch Liquid Retina, MagSafe, fanless design.",             "price": 114900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=macbook+air+m3"},
        {"store": "Flipkart",         "title": "Apple MacBook Air 13 M3 8GB 256GB Midnight",    "description": "M3 chip, Liquid Retina display, MagSafe 3, 18-hour battery.",                          "price": 113990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=macbook+air+m3"},
        {"store": "Croma",            "title": "Apple MacBook Air 13\" M3 8GB 256GB",           "description": "M3, Liquid Retina, MagSafe 3, 18hr battery, fanless. In-store available.",            "price": 114900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=macbook+air+m3"},
        {"store": "Reliance Digital", "title": "Apple MacBook Air M3 13-inch 8GB 256GB",        "description": "Fanless M3, 18hr battery, Liquid Retina, MagSafe charging.",                          "price": 114900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=macbook+air+m3"},
        {"store": "Tata CLiQ",        "title": "Apple MacBook Air 13-inch M3 Midnight",         "description": "M3 chip, 18hr battery, Liquid Retina. Easy EMI options.",                             "price": 112999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=macbook+air+m3"},
        {"store": "Vijay Sales",      "title": "Apple MacBook Air 13 M3 8GB 256GB Midnight",    "description": "M3 processor, fanless, Liquid Retina, MagSafe. No-cost EMI.",                         "price": 114900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/macbook-air-m3"},
        {"store": "eBay IN",          "title": "Apple MacBook Air M3 13 8GB 256GB Midnight",    "description": "Sealed Indian model. M3, Liquid Retina, MagSafe 3.",                                  "price": 109999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=macbook+air+m3"},
        {"store": "Snapdeal",         "title": "Apple MacBook Air 13-inch M3 8GB",              "description": "M3 chip, fanless design, 18hr battery. Fast delivery.",                                "price": 111999.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.snapdeal.com/search?keyword=macbook+air+m3"},
    ],
    "airpods": [
        {"store": "Amazon IN",        "title": "Apple AirPods Pro 2nd Gen USB-C MagSafe",       "description": "ANC, Adaptive Audio, H2 chip, 6hr + 30hr case, IPX4.",                                "price": 24900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=airpods+pro+2"},
        {"store": "Flipkart",         "title": "Apple AirPods Pro 2nd Generation",              "description": "H2 chip, ANC, Adaptive Transparency, Personalised Spatial Audio.",                    "price": 24900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=airpods+pro+2"},
        {"store": "Croma",            "title": "Apple AirPods Pro 2nd Gen USB-C",               "description": "ANC, USB-C MagSafe, Adaptive Audio, 30hr total battery.",                             "price": 24900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=airpods+pro+2"},
        {"store": "Reliance Digital", "title": "Apple AirPods Pro 2nd Generation",              "description": "ANC, H2 chip, MagSafe USB-C, 30hr total battery.",                                   "price": 24900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=airpods+pro+2"},
        {"store": "Tata CLiQ",        "title": "Apple AirPods Pro 2nd Gen",                     "description": "ANC, Adaptive Audio, MagSafe USB-C. Easy EMI available.",                            "price": 23999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=airpods+pro+2"},
        {"store": "Vijay Sales",      "title": "Apple AirPods Pro 2nd Generation USB-C",        "description": "H2 chip, ANC, Adaptive Audio. No-cost EMI on select cards.",                         "price": 24900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/airpods-pro-2"},
        {"store": "eBay IN",          "title": "Apple AirPods Pro 2nd Gen Sealed",              "description": "Sealed Indian model. ANC, H2, MagSafe USB-C.",                                       "price": 22999.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=airpods+pro+2"},
        {"store": "Snapdeal",         "title": "Apple AirPods Pro 2nd Generation",              "description": "H2 chip, ANC, Adaptive Transparency. Fast shipping.",                                "price": 23490.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.snapdeal.com/search?keyword=airpods+pro+2"},
    ],
    "tv": [
        {"store": "Amazon IN",        "title": "LG OLED55C3PSA 55\" OLED 4K Smart TV",         "description": "OLED evo, a9 AI Gen6, Dolby Vision IQ, 120Hz, HDMI 2.1, webOS 23.",                   "price": 129990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=lg+oled+55+c3"},
        {"store": "Flipkart",         "title": "LG 55\" OLED C3 4K Smart TV",                  "description": "OLED evo panel, a9 AI Processor Gen6, 120Hz, 4x HDMI 2.1.",                          "price": 127990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=lg+oled+55+c3"},
        {"store": "Croma",            "title": "LG OLED55C3 55\" 4K OLED Smart TV",            "description": "OLED evo, Dolby Vision, 120Hz, webOS 23. Available for in-store pickup.",             "price": 129990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=lg+oled+55+c3"},
        {"store": "Reliance Digital", "title": "LG 55\" C3 OLED 4K TV",                        "description": "OLED evo, a9 Gen 6, 4K, 120Hz. Exchange offer available.",                           "price": 129990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=lg+oled+55+c3"},
        {"store": "Tata CLiQ",        "title": "LG OLED55C3PSA 55\" OLED TV",                  "description": "OLED evo, a9 AI, 120Hz, Dolby Vision. EMI starting ₹10,832/month.",                  "price": 124999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=lg+oled+55+c3"},
        {"store": "Vijay Sales",      "title": "LG 55\" OLED C3 4K Smart TV",                  "description": "OLED evo panel, 4K, 120Hz, Dolby Vision IQ, webOS. No-cost EMI.",                   "price": 128990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/lg-oled-55-c3"},
        {"store": "eBay IN",          "title": "LG 55 C3 OLED 4K Smart TV",                    "description": "Indian model, OLED evo, 120Hz, Dolby Vision IQ.",                                     "price": 119999.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=lg+oled+55+c3"},
        {"store": "Snapdeal",         "title": "LG 55\" OLED 4K C3 Smart TV",                  "description": "OLED evo, 4K, a9 AI Gen6, 120Hz, webOS 23.",                                        "price": 122999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.snapdeal.com/search?keyword=lg+oled+55+c3"},
    ],
    "laptop": [
        {"store": "Amazon IN",        "title": "Lenovo IdeaPad Slim 5 15.6\" Core i5 16GB 512GB","description": "15.6-inch FHD IPS, Intel i5-13420H, 16GB RAM, 512GB NVMe, Windows 11.",            "price": 62990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=lenovo+ideapad+slim+5+i5"},
        {"store": "Flipkart",         "title": "HP 15s 15.6\" Intel Core i5 16GB 512GB SSD",   "description": "15.6-inch FHD, Intel i5, 16GB, 512GB SSD, HP Fast Charge, Windows 11.",             "price": 58990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=hp+15s+i5+laptop"},
        {"store": "Croma",            "title": "Dell Inspiron 15 3520 Core i5 16GB 512GB",     "description": "15.6-inch FHD, Intel Core i5, 16GB, 512GB SSD. Available in-store.",                "price": 67990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=dell+inspiron+15+i5"},
        {"store": "Reliance Digital", "title": "ASUS VivoBook 15 Core i5 16GB 512GB",          "description": "OLED FHD display, Intel i5, 16GB, 512GB SSD. In-store and online.",                 "price": 65990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=asus+vivobook+15+i5"},
        {"store": "Tata CLiQ",        "title": "Lenovo IdeaPad Slim 3 15.6\" i5 16GB 512GB",   "description": "Intel Core i5, 16GB RAM, 512GB SSD, Windows 11. EMI options.",                     "price": 60999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=lenovo+ideapad+i5+laptop"},
        {"store": "Vijay Sales",      "title": "Acer Aspire 5 15.6\" Core i5 16GB 512GB",      "description": "IPS FHD, Intel i5, 16GB, 512GB NVMe, Windows 11. No-cost EMI.",                    "price": 59990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/acer-aspire-5-i5"},
        {"store": "eBay IN",          "title": "Lenovo ThinkPad E15 i5 16GB 512GB Refurb",     "description": "Grade A refurbished, Core i5, 16GB, 512GB SSD.",                                    "price": 45999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=lenovo+thinkpad+e15+i5"},
        {"store": "Snapdeal",         "title": "HP Pavilion 15 Core i5 16GB 512GB",            "description": "15.6-inch FHD, Intel Core i5, 16GB, 512GB SSD. Fast delivery.",                    "price": 63490.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.snapdeal.com/search?keyword=hp+pavilion+i5+laptop"},
    ],
    "headphones": [
        {"store": "Amazon IN",        "title": "Sony WH-1000XM5 Wireless Noise Cancelling",    "description": "Industry-leading ANC, 30hr battery, multipoint pairing, LDAC Hi-Res.",               "price": 26990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=sony+wh-1000xm5"},
        {"store": "Flipkart",         "title": "Sony WH-1000XM5 Over-Ear Headphones",          "description": "Best-in-class ANC, 30hr battery, multipoint, speak-to-chat, LDAC.",                 "price": 26990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=sony+wh-1000xm5"},
        {"store": "Croma",            "title": "Sony WH-1000XM5 Wireless Headphones Black",    "description": "Best ANC, 30hr battery, LDAC Hi-Res Audio. Available in-store.",                    "price": 26990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=sony+wh-1000xm5"},
        {"store": "Reliance Digital", "title": "Sony WH-1000XM5 Wireless NC Headphones",       "description": "Industry-leading ANC, 30hr battery, LDAC. Exchange offers available.",              "price": 26990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=sony+wh-1000xm5"},
        {"store": "Tata CLiQ",        "title": "Sony WH-1000XM5 Headphones",                   "description": "Best-in-class ANC, 30hr battery, multipoint. EMI available.",                       "price": 25999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=sony+wh-1000xm5"},
        {"store": "Vijay Sales",      "title": "Sony WH-1000XM5 Over-Ear Headphones",          "description": "30hr ANC, LDAC, multipoint Bluetooth. No-cost EMI.",                               "price": 26990.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/sony-wh-1000xm5"},
        {"store": "eBay IN",          "title": "Sony WH-1000XM5 Headphones Brand New",          "description": "New sealed Indian model. Best ANC, 30hr battery.",                                  "price": 23999.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=sony+wh+1000xm5"},
        {"store": "Snapdeal",         "title": "Sony WH-1000XM5 Wireless Headphones",          "description": "Industry-leading ANC, 30hr battery, LDAC. Fast delivery.",                          "price": 25490.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.snapdeal.com/search?keyword=sony+wh-1000xm5"},
    ],
    "watch": [
        {"store": "Amazon IN",        "title": "Apple Watch Series 9 GPS 41mm Midnight",       "description": "S9 chip, double-tap, 18hr battery, always-on Retina, ECG, crash detection.",         "price": 41900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.amazon.in/s?k=apple+watch+series+9"},
        {"store": "Flipkart",         "title": "Apple Watch Series 9 GPS 41mm",                "description": "S9 SiP, double tap, always-on Retina, 18hr battery, ECG, crash detection.",         "price": 41900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.flipkart.com/search?q=apple+watch+series+9"},
        {"store": "Croma",            "title": "Apple Watch Series 9 GPS 41mm Midnight",       "description": "S9 chip, double tap, always-on Retina, ECG. In-store pickup available.",            "price": 41900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.croma.com/searchB?q=apple+watch+series+9"},
        {"store": "Reliance Digital", "title": "Apple Watch Series 9 GPS 41mm",                "description": "S9 chip, double tap, crash detection. Exchange offers available.",                   "price": 41900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.reliancedigital.in/search?q=apple+watch+series+9"},
        {"store": "Tata CLiQ",        "title": "Apple Watch Series 9 GPS 41mm Midnight",       "description": "S9, double tap, ECG, always-on Retina. Easy EMI starting ₹3,491/month.",            "price": 40999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.tatacliq.com/search/?searchCategory=all&text=apple+watch+series+9"},
        {"store": "Vijay Sales",      "title": "Apple Watch Series 9 GPS 41mm",                "description": "S9, always-on display, ECG, crash detection. No-cost EMI.",                         "price": 41900.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.vijaysales.com/search/apple-watch-series-9"},
        {"store": "eBay IN",          "title": "Apple Watch Series 9 GPS 41mm Sealed",         "description": "Sealed Indian model. S9 chip, always-on Retina.",                                   "price": 38999.00, "currency": "INR", "in_stock": True,  "region": "in", "url": "https://www.ebay.in/sch/i.html?_nkw=apple+watch+series+9"},
        {"store": "Snapdeal",         "title": "Apple Watch Series 9 GPS 41mm Midnight",       "description": "S9 chip, double tap gesture, ECG. Fast shipping.",                                  "price": 40490.00, "currency": "INR", "in_stock": False, "region": "in", "url": "https://www.snapdeal.com/search?keyword=apple+watch+series+9"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD SYNONYMS (global)
# ─────────────────────────────────────────────────────────────────────────────
KEYWORD_SYNONYMS = {
    "phone": ["iphone", "samsung"],
    "mobile": ["iphone", "samsung"],
    "smartphone": ["iphone", "samsung"],
    "console": ["ps5"],
    "playstation": ["ps5"],
    "gaming": ["ps5"],
    "mac": ["macbook"],
    "apple laptop": ["macbook"],
    "macbook air": ["macbook"],
    "macbook pro": ["macbook"],
    "buds": ["airpods"],
    "earphones": ["airpods", "headphones"],
    "earbuds": ["airpods"],
    "wireless earbuds": ["airpods"],
    "vacuum": ["dyson"],
    "hoover": ["dyson"],
    "cordless vacuum": ["dyson"],
    "ipad": ["tablet"],
    "oled tv": ["tv"],
    "smart tv": ["tv"],
    "television": ["tv"],
    "sony headphones": ["headphones"],
    "bose": ["headphones"],
    "apple watch": ["watch"],
    "smartwatch": ["watch"],
}

ALL_PRODUCTS = {
    "uk": UK_PRODUCTS,
    "us": US_PRODUCTS,
    "in": IN_PRODUCTS,
}


def _get_mock_results(query: str, region: str = "all") -> List[dict]:
    """Return results for query and region. Empty list if not found."""
    q = query.lower().strip()
    results = []

    regions_to_search = [region] if region in ALL_PRODUCTS else list(ALL_PRODUCTS.keys())

    def _find_in_db(db: dict) -> List[dict]:
        # Direct key match
        for key, products in db.items():
            if key in q or q in key:
                return [p.copy() for p in products]
        # Synonym match
        for synonym, keys in KEYWORD_SYNONYMS.items():
            if synonym in q:
                for key in keys:
                    if key in db:
                        return [p.copy() for p in db[key]]
        # Word-by-word
        for word in q.split():
            if len(word) < 3:
                continue
            for key, products in db.items():
                if word in key or key in word:
                    return [p.copy() for p in products]
        return []

    for r in regions_to_search:
        db = ALL_PRODUCTS.get(r, {})
        found = _find_in_db(db)
        results.extend(found)

    return results


class SearchService:
    @staticmethod
    async def search_all_stores(query: str, region: str = "all") -> List[dict]:
        """
        Search across stores for given query and region.
        region: 'uk', 'us', 'in', or 'all'
        Returns empty list when product genuinely not found.
        """
        results = []

        # Try live scrapers for UK stores only (others need API keys)
        if region in ("uk", "all"):
            scrapers = [AmazonScraper, ArgosScraper, CurrysScraper, EbayScraper]
            for scraper_cls in scrapers:
                try:
                    store_results = await scraper_cls.search(query)
                    for item in store_results:
                        item["price"] = normalize_price(item.get("price", "0"))
                        item.setdefault("region", "uk")
                        item.setdefault("currency", "GBP")
                        results.append(item)
                except Exception as e:
                    logger.warning(f"[{scraper_cls.__name__}] failed: {e}")

        # Fall back to mock data when live scrapers return nothing
        if not results:
            logger.info(f"[SearchService] Using mock data for '{query}' region='{region}'")
            results = _get_mock_results(query, region)

        return results
