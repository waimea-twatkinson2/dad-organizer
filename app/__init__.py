#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
     with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT * FROM tasks ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        tasks = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", tasks=tasks)



#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/item/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM tasks WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            item = result.rows[0]
            return render_template("pages/item.jinja", item=item)

        else:
            # No, so show error
            return not_found_error()
        
@app.get("/edit/<int:id>")
def edit_task(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM tasks WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            item = result.rows[0]
            return render_template("pages/edit.jinja", item=item)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    client = request.form.get("client")
    location = request.form.get("location")
    description = request.form.get("description")
    urgency = request.form.get("urgency")
    due_date = request.form.get("due_date")

    # Sanitize the text inputs
    name = html.escape(name)
    client = html.escape(client)
    location = html.escape(location)
    description = html.escape(description)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO tasks (name, urgency, client, location, description, due_date) VALUES (?, ?, ?, ?, ?, ?)"
        params = [name, urgency, client, location, description, due_date]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Task, '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_task(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM tasks WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Task deleted", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for completing a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/complete/<int:id>")
def complete_a_task(id):
    with connect_db() as client:
        # Complete the thing from the DB
        sql = "UPDATE tasks SET completed=1 WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Task completed", "success")
        return redirect("/")
    
@app.get("/uncomplete/<int:id>")
def uncomplete_a_task(id):
    with connect_db() as client:
        # Complete the thing from the DB
        sql = "UPDATE tasks SET completed=0 WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Task uncompleted", "success")
        return redirect("/")