from bs4 import BeautifulSoup
import requests, time
from splinter import Browser
import pandas


def scrape():
    #Setting URLS for gathering Latest News, JPL Image, twitter for weather, facts, and images of hemisphere 
    mars_news_url = "https://mars.nasa.gov/news/"
    jpl_featured_image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    twitter_url = "https://twitter.com/marswxreport?lang=en"
    facts_url = 'https://space-facts.com/mars/'
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    response = requests.get(mars_news_url)
    soup = BeautifulSoup(response.text, 'lxml')

    #Latest News Article Title and teaser
    title = soup.find('div', class_='content_title').text
    article_teaser = soup.find('div', class_='rollover_description_inner').text


    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    browser.visit(jpl_featured_image_url)

    image_soup = BeautifulSoup(browser.html, "html.parser")
    #the url for the JPL image
    image_url = "https://www.jpl.nasa.gov" + image_soup.find('a', id="full_image").get("data-fancybox-href")

    #gathering weather data from twitter
    browser.visit(twitter_url)
    time.sleep(2)
    weather_soup = BeautifulSoup(browser.html, "html.parser")
    weather_tweet = weather_soup.find_all("span", class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")
    mars_weather = weather_tweet[27].text

    #getting the facts
    browser.visit(facts_url)
    mars_facts_html = BeautifulSoup(browser.html, "html.parser")
    mars_table = mars_facts_html.find("table", class_="tablepress tablepress-id-p-mars")

    #converting the table into a dataframe
    mars_df = pandas.read_html(str(mars_table))

    #setting up a variable for the facts table
    mars_df_table = mars_df[0]

    #updating the columns names
    mars_df_table.rename(columns = {0: "Description",
                                    1: "Value"},
                        inplace = True)
    #exporting the table as an html object
    mars_table_html = mars_df_table.to_html(index = False,
                                            header = False,
                                            border = 0,
                                            classes = "table-hover table-responsive-lg",
                                            )

    #Gathering hemishphere data
    browser.visit(hemispheres_url)
    time.sleep(0.5)

    hemispheres = BeautifulSoup(browser.html, "html.parser")
    hemisphere_list = hemispheres.find_all("h3")

    hemisphere_image_urls = []

    for x in range(0, len(hemisphere_list)):
        browser.click_link_by_partial_text(hemisphere_list[x].text)
        hemisphere_soup = BeautifulSoup(browser.html,"html.parser")
        hemisphere_dict = {"title":hemisphere_soup.find('h2').text.rsplit(' ', 1)[0],
                           "img_url":hemisphere_soup.find_all('li')[0].find('a').get("href")   
        }
        hemisphere_image_urls.append(hemisphere_dict)
        time.sleep(0.5)
        browser.back()

    browser.quit()

    mars_scraped_data = {
        "article_title":title,
        "article_teaser": article_teaser,
        "JPL_image":image_url,
        "weather": mars_weather,
        "facts_table":mars_table_html,
        "hemispheres":hemisphere_image_urls
    }
    return mars_scraped_data
