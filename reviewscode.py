from flaskapp import *

### Most of the code in this file is modified ChatGPT code ###

# Prompt the user for a username
# Then redirect to the add review page
@app.route("/add_review", methods=["GET", "POST"])
def add_review_redirect():
    if request.method == "GET":
        return render_template("ask_username.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        if username:
            return redirect(url_for("add_review", username=username))
        else:
            return render_template("review_error.html", error="Username is required")

# Add the review to the database
@app.route("/add_review/<username>", methods=["GET", "POST"])
def add_review(username):
    try:
        # Check if the user exists in DynamoDB
        response = table.get_item(Key={"username": username})

        if "Item" not in response:
            return render_template("review_error.html", error="User not found")

        if request.method == "GET":
            return render_template("add_review.html", username=username)

        elif request.method == "POST":
            title = request.form.get("title")
            rating = request.form.get("rating")
            review_text = request.form.get("review_text")
            spoiler = request.form.get("spoiler") == "yes"

            if not all([title, rating, review_text]):
                return render_template("review_error.html", error="Missing fields")

            # Check if movie exists in SQL
            result = execute_query("SELECT 1 FROM movie WHERE title = %s", (title,))
            if not result:
                return render_template("review_error.html", error="Movie not found")

            # Get current user data
            response = table.get_item(Key={"username": username})
            if "Item" not in response:
                return render_template("review_error.html", error="User not found")

            # Check if a review for the movie already exists
            existing_reviews = response["Item"].get("reviews", [])
            for r in existing_reviews:
                try:
                    if r["M"]["title"]["S"] == title:
                        return render_template("review_error.html", error=f"You've already reviewed '{title}'")
                except (KeyError, TypeError):
                    continue  # skip malformed reviews

            # Construct new review
            new_review = {
                "M": {
                    "title": {"S": title},
                    "rating": {"N": str(rating)},
                    "review_text": {"S": review_text},
                    "spoiler": {"BOOL": spoiler}
                }
            }

            # Append to user's reviews
            table.update_item(
                Key={"username": username},
                UpdateExpression="SET reviews = list_append(if_not_exists(reviews, :empty), :r)",
                ExpressionAttributeValues={
                ":r": [new_review],
                ":empty": []
                },
    ReturnValues="UPDATED_NEW"
)
            return render_template("review_success.html", username=username, title=title)

    except ClientError as e:
        return render_template("review_error.html", error=e.response["Error"]["Message"])
    except Exception as e:
        return render_template("review_error.html", error=str(e))


# Prompt the user for a username
# Then redirect to the delete review page
@app.route("/delete_review", methods=["GET", "POST"])
def delete_review_redirect():
    if request.method == "GET":
        return render_template("ask_username_delete.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        if username:
            return redirect(url_for("delete_review", username=username))
        else:
            return render_template("review_error.html", error="Username is required")

# Delete a review from the database
@app.route("/delete_review/<username>", methods=["GET", "POST"])
def delete_review(username):
    try:
        # Check user exists
        response = table.get_item(Key={"username": username})
        if "Item" not in response:
            return render_template("review_error.html", error="User not found")

        if request.method == "GET":
            return render_template("delete_review.html", username=username)

        elif request.method == "POST":
            title_to_delete = request.form.get("title")
            if not title_to_delete:
                return render_template("review_error.html", error="Title required")

            # Load raw reviews from DynamoDB
            raw_reviews = response["Item"].get("reviews", [])

            # Track if we found a review to delete
            found = False
            updated_reviews = []

            for r in raw_reviews:
                try:
                    review_title = r["M"]["title"]["S"]
                    if review_title != title_to_delete:
                        updated_reviews.append(r)
                    else:
                        found = True  # found a match to delete
                except (KeyError, TypeError):
                    updated_reviews.append(r)

            if not found:
                return render_template("review_error.html", error=f"No review found for '{title_to_delete}'")

            # Update DynamoDB
            table.update_item(
                Key={"username": username},
                UpdateExpression="SET reviews = :r",
                ExpressionAttributeValues={":r": updated_reviews},
                ReturnValues="UPDATED_NEW"
            )
            
            return render_template("review_success.html", username=username, title=title_to_delete + " (deleted)")



    except Exception as e:
        return render_template("review_error.html", error=str(e))

# Prompt the user for a username
# Then redirect to the update review page
@app.route("/update_review", methods=["GET", "POST"])
def update_review_redirect():
    if request.method == "GET":
        return render_template("ask_username_update.html")
    
    elif request.method == "POST":
        username = request.form.get("username")
        if username:
            return redirect(url_for("update_review", username=username))
        else:
            return render_template("review_error.html", error="Username is required")


# Update a review in the database
@app.route("/update_review/<username>", methods=["GET", "POST"])
def update_review(username):
    try:
        # Get the user's data
        response = table.get_item(Key={"username": username})
        if "Item" not in response:
            return render_template("review_error.html", error="User not found")

        reviews = response["Item"].get("reviews", [])

        if request.method == "GET":
            # Show dropdown to pick a movie to update
            titles = []
            for r in reviews:
                try:
                    titles.append(r["M"]["title"]["S"])
                except:
                    continue
            return render_template("choose_review_update.html", username=username, titles=titles)

        elif request.method == "POST":
            title = request.form.get("title")
            new_rating = request.form.get("rating")
            new_text = request.form.get("review_text")
            new_spoiler = request.form.get("spoiler") == "yes"

            # Rebuild updated review list
            updated_reviews = []
            found = False

            for r in reviews:
                try:
                    review_title = r["M"]["title"]["S"]
                    if review_title == title:
                        # Replace with new review
                        updated_reviews.append({
                            "M": {
                                "title": {"S": title},
                                "rating": {"N": str(new_rating)},
                                "review_text": {"S": new_text},
                                "spoiler": {"BOOL": new_spoiler}
                            }
                        })
                        found = True
                    else:
                        updated_reviews.append(r)
                except:
                    updated_reviews.append(r)

            if not found:
                return render_template("review_error.html", error=f"No review for '{title}' found")

            # Update DynamoDB
            table.update_item(
                Key={"username": username},
                UpdateExpression="SET reviews = :r",
                ExpressionAttributeValues={":r": updated_reviews},
                ReturnValues="UPDATED_NEW"
            )

            return render_template("review_success.html", username=username, title=title + " (updated)")

    except Exception as e:
        return render_template("review_error.html", error=str(e))

# Display all reviews   
@app.route("/display_review", methods=["GET", "POST"])
def all_reviews():
    if request.method == "GET":
        # Ask user whether they want to see spoilers
        return render_template("ask_spoilers.html")

    elif request.method == "POST":
        show_spoilers = request.form.get("show_spoilers") == "yes"

        try:
            response = table.scan()
            items = response.get("Items", [])
            reviews_list = []

            for user in items:
                username = user.get("username", "Unknown")
                user_reviews = user.get("reviews", [])
                
                for r in user_reviews:
                    try:
                        r_data = r["M"]
                        if not show_spoilers and r_data["spoiler"]["BOOL"]:
                            continue  # Skip spoiler reviews
                        
                        reviews_list.append({
                            "username": username,
                            "title": r_data["title"]["S"],
                            "rating": r_data["rating"]["N"],
                            "spoiler": r_data["spoiler"]["BOOL"],
                            "text": r_data["review_text"]["S"]
                        })
                    except (KeyError, TypeError):
                        continue

            return render_template("display_review.html", reviews=reviews_list)

        except Exception as e:
            return render_template("review_error.html", error=str(e))

# Add a new user to the database        
@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "GET":
        return render_template("new_user.html")

    elif request.method == "POST":
        username = request.form.get("username")
        if not username:
            return render_template("review_error.html", error="Username is required")

        # Check if the user already exists
        try:
            response = table.get_item(Key={"username": username})
            if "Item" in response:
                return render_template("review_error.html", error="Username already exists")

            # Create new user
            table.put_item(Item={
                "username": username,
                "reviews": []
            })

            return render_template("new_user_success.html", username=username)

        except Exception as e:
            return render_template("review_error.html", error=str(e))

