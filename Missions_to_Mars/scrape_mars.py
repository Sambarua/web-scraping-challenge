# Jupyter Notebook Conversion to Python Script
#################################################

# Dependencies and Setup
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import datetime as dt
import pymongo
import requests
from webdriver_manager.chrome import ChromeDriverManager




# DB Setup
# 
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars


#################################################
# Mac
#################################################
# Set Executable Path & Initialize Chrome Browser

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)



#################################################
# NASA Mars News
#################################################
def mars_news(browser):
    # Visit the NASA Mars News Site
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get First List Item & Wait Half a Second If Not Immediately Present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)
    
    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    # Parse Results HTML with BeautifulSoup
    # Find Everything Inside:
    #   <ul class="item_list">
    #     <li class="slide">
    try:
        slide_element = news_soup.select_one("ul.item_list li.slide")
        slide_element.find("div", class_="content_title")

        # Scrape the Latest News Title
        # Use Parent Element to Find First <a> Tag and Save it as news_title
        news_title = slide_element.find("div", class_="content_title").get_text()

        news_paragraph = slide_element.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    return news_title, news_paragraph


#################################################
# JPL Mars Space Images - Featured Image
#################################################
# NASA JPL (Jet Propulsion Laboratory) Site Web Scraper
def featured_image(browser):
    # Visit the NASA JPL (Jet Propulsion Laboratory) Site
    url = "https://spaceimages-mars.com/"
    browser.visit(url)

    # Ask Splinter to Go to Site and Click Button with Class Name full_image
    
    html_img = browser.html
    soup_img = BeautifulSoup(html_img, 'html.parser')

    # Find "More Info" Button and Click I

    featured_image = soup_img.find('img', class_="headerimage fade-in")
    featured_image_url = url+featured_image['src']
    print(featured_image_url)

    img = soup_img.select_one("figure.lede a img")
    try:
        img_url = img.get("src")
    except AttributeError:
        return None 
   # Use Base URL to Create Absolute URL
    img_url = f"https://spaceimages-mars.com{img_url}"
    return img_url



#################################################
# Mars Facts
#################################################
# Mars Facts Web Scraper
# Visit the Mars Facts Site Using Pandas to Read
mars_facts = pd.read_html("https://galaxyfacts-mars.com/")[0]
print(mars_facts)
mars_facts.reset_index(inplace=True)
mars_facts.columns=["ID", "Properties", "Mars", "Earth"]
mars_facts
mars_facts.drop(columns=mars_facts.columns[0], axis=1, inplace=True)
mars_facts
mars_facts_html = mars_facts.to_html(header=False, index=False)
mars_facts_html

#################################################
# Mars Hemispheres
#################################################
# Mars Hemispheres Web Scraper
def hemisphere(browser):
    # Visit the USGS Astrogeology Science Center Site
    url = "https://marshemispheres.com/"
    browser.visit(url)

    hemisphere_image_urls = []

    # Get a List of All the Hemisphere
    links = browser.find_by_css("a.product-item h3")
    for item in range(len(links)):
        hemisphere = {}
        
        # Find Element on Each Loop to Avoid a Stale Element Exception
        browser.find_by_css("a.product-item h3")[item].click()
        
        # Find Sample Image Anchor Tag & Extract <href>
        sample_element = browser.find_link_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        
        # Get Hemisphere Title
        hemisphere["title"] = browser.find_by_css("h2.title").text
        
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemisphere)
        
        # Navigate Backwards
        browser.back()
    return hemisphere_image_urls

# Helper Function
def scrape_hemisphere(html_text):
    hemisphere_soup = BeautifulSoup(html_text, "html.parser")
    try: 
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_element = None
        sample_element = None 
    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemisphere


#################################################
# Main Web Scraping Bot
#################################################
def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser("chrome", **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    img_url = featured_image(browser)
    facts = mars_facts
    hemisphere_image_urls = hemisphere(browser)
    timestamp = dt.datetime.now()

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": img_url,
        "facts": facts,
        "hemispheres": hemisphere_image_urls,
        "last_modified": timestamp
    }
    browser.quit()
    return data 

if __name__ == "__main__":
    print(scrape_all())