import csv
import time
import re 
import os
from bs4 import BeautifulSoup
from httpcore import TimeoutException
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class FlipkartScrapper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def try_close_popup(self, driver):
        popup_selectors = [
            "//button[contains(text(), 'x')]",
            "//button[contains(@aria-label, 'Close')]",
            "//button[contains(@class, 'close')]",
            "//div[@role='dialog']//button"
        ]

        for xpath in popup_selectors:
            try:
                close_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                close_btn.click()
                print(f"✅ Popup closed using: {xpath}")
                return True
            except TimeoutException:
                continue

        print("❗ No close button found.")
        return False
   
    
    def get_top_reviews(self, product_url, count=2):
        options = uc.ChromeOptions()
        #options.binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome"
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options, use_subprocess=True, 
                           browser_executable_path="/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta")

        if not product_url.startswith("http"):
            return "No reviews found"
        
        try:
            driver.get(product_url)
            time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
                #self.try_close_popup(driver)
                time.sleep(1)
            except Exception as e:
                print(f"Error occurred while closing popup: {e}")
            
            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_blocks = soup.select("div._27M-vq, div.col.EPCmJX, div._6K-7Co")
#                                        "div._27M-vq, div.col.EPCmJX, div._6K-7Co"
            seen = set()
            reviews = []
            
            for block in review_blocks:
                text = block.get_text(separator=" ", strip=True)
                if text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= count:
                    break
        except Exception as e:
            reviews = []
        
        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"


    
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, use_subprocess=True, 
                           browser_executable_path="/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta")
        # search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except Exception as e:
            print(f"Error occurred while closing popup: {e}")
        
        time.sleep(2)
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        for item in items:
            try:
                product_title = item.find_element(By.CSS_SELECTOR, "div.KzDlHZ").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "div.Nx9bqj._4b5DiR").text.strip()
                rating = item.find_element(By.CSS_SELECTOR, "div.XQDdHH").text.strip()
                reviews_text = item.find_element(By.CSS_SELECTOR, "span.Wphh3N").text.strip()
                # match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = int(match.group(0).replace(',', '')) if match else 0

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                # match = re.findall(r"/p/itm[0-9a-zA-Z]+)", href)
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"
                #<a class="CGtC98" target="_blank" rel="noopener noreferrer" href="/apple-iphone-16-black-128-gb/p/itmb07d67f995271?pid=MOBH4DQFG8NKFRDY&amp;lid=LSTMOBH4DQFG8NKFRDYNBDOZI&amp;marketplace=FLIPKART&amp;q=iphone+16&amp;store=tyy%2F4io&amp;srno=s_1_1&amp;otracker=search&amp;otracker1=search&amp;fm=organic&amp;iid=4ab9e772-087a-48c7-acf1-cf67c6f21ee6.MOBH4DQFG8NKFRDY.SEARCH&amp;ppt=hp&amp;ppn=homepage&amp;ssid=06m2tlsdcg0000001758270748244&amp;qH=9ea15d2374058112"><div class="Otbq5D"><div class="yPq5Io"><div><div class="_4WELSP" style="height: 200px; width: 200px;"><img loading="eager" class="DByuf4" alt="Apple iPhone 16 (Black, 128 GB)" src="https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/8/w/5/-original-imah4jyfwr3bfjbg.jpeg?q=70"></div></div><div class="DShtpz"><span class="Y9obZf">Coming Soon</span></div></div><div class="qaR90o"><div class="A8uQAd"><span class="Lni97G"><label class="tJjCVx"><input type="checkbox" class="vn9L2C" readonly=""><div class="XqNaEv"></div></label></span><label class="uu79Xy"><span>Add to Compare</span></label></div></div><div class="oUss6M ssUU08"><div class="+7E521"><svg xmlns="http://www.w3.org/2000/svg" class="N1bADF" width="16" height="16" viewBox="0 0 20 16"><path d="M8.695 16.682C4.06 12.382 1 9.536 1 6.065 1 3.219 3.178 1 5.95 1c1.566 0 3.069.746 4.05 1.915C10.981 1.745 12.484 1 14.05 1 16.822 1 19 3.22 19 6.065c0 3.471-3.06 6.316-7.695 10.617L10 17.897l-1.305-1.215z" fill="#2874F0" class="x1UMqG" stroke="#FFF" fill-rule="evenodd" opacity=".9"></path></svg></div></div></div><div class="yKfJKb row"><div class="col col-7-12"><div class="KzDlHZ">Apple iPhone 16 (Black, 128 GB)</div><div class="_5OesEi"><span id="productRating_LSTMOBH4DQFG8NKFRDYNBDOZI_MOBH4DQFG8NKFRDY_" class="Y1HWO0"><div class="XQDdHH">4.6<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMyIgaGVpZ2h0PSIxMiI+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTYuNSA5LjQzOWwtMy42NzQgMi4yMy45NC00LjI2LTMuMjEtMi44ODMgNC4yNTQtLjQwNEw2LjUuMTEybDEuNjkgNC4wMSA0LjI1NC40MDQtMy4yMSAyLjg4Mi45NCA0LjI2eiIvPjwvc3ZnPg==" class="Rza2QY"></div></span><span class="Wphh3N"><span><span>19,106 Ratings&nbsp;</span><span class="hG7V+4">&amp;</span><span>&nbsp;793 Reviews</span></span></span></div><div class="_6NESgJ"><ul class="G4BRas"><li class="J+igdf">128 GB ROM</li><li class="J+igdf">15.49 cm (6.1 inch) Super Retina XDR Display</li><li class="J+igdf">48MP + 12MP | 12MP Front Camera</li><li class="J+igdf">A18 Chip, 6 Core Processor Processor</li><li class="J+igdf">1 year warranty for phone and 1 year warranty for in Box Accessories.</li></ul></div></div><div class="col col-5-12 BfVC2z"><div class="cN1yYO"><div class="hl05eU"><div class="Nx9bqj _4b5DiR">₹51,999</div><div class="yRaY8j ZYYwLA">₹69,999</div><div class="UkUFwK"><span>25% off</span></div></div></div><div class="_0CSTHy"><img height="21" src="//static-assets-web.flixcart.com/fk-p-linchpin-web/fk-cp-zion/img/fa_9e47c1.png"></div></div></div></a>
            except Exception as e:
                print(f"Error occurred while processing item: {e}")
                continue

            top_reviews = self.get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, product_title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products 
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
        print(f"Saving data to {filename}...")
        if os.path.isabs(filename):
            path = filename
        elif os.path.dirname(filename):
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            path = os.path.join(self.output_dir, filename)
        
        print(f"Resolved path: {path}")
        
        with open(path, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)



    
