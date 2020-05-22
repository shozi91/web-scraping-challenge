from scrape_mars import scrape
import pymongo
from flask import Flask, render_template,redirect

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db

# Creates a collection in the database and inserts two documents
@app.route('/scrape')
def mars_scrape():
    data = scrape()
    # Drops collection if available to remove duplicates
    db.mars_data.drop()
    db.mars_data.insert_many([data])
    print(data)
    return redirect("/")


# Set route
@app.route('/')
def index():
    # Store the entire team collection in a list
    mars_data = list(db.mars_data.find())
    

    # Return the template with the teams list passed in
    return render_template('index.html',mars_data = mars_data)


if __name__ == "__main__":
    app.run(debug=True)
