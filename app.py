from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
import pandas as pd
import sqlite3
import re
import random
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def format_word(word):
    first_letter = word[0].upper()
    rest_of_word = word[1:].lower()
    return first_letter + rest_of_word

def format_age(years, months):
    if years == 0:
        if(months == 1):
            return f"1 month"
        else:
            return f"{months} months"
    elif years == 1:
        if(months == 0):
            return f"{years} year"
        else:
            return f"{years} year, {months} months"
    else:
        if(months == 0):
            return f"{years} years"
        else:
            return f"{years} years, {months} months"

def generate_ID():
    with sqlite3.connect("available_dogs.db") as conn:
        while True:
            characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            dog_ID = ''.join(random.choices(characters, k=5))

            exists = conn.execute(
                "SELECT 1 FROM available_dogs WHERE ID = ?",
                (dog_ID,)
            ).fetchone()

            if not exists:
                return dog_ID

def valid_dog_id(dog_ID):
    return bool(re.fullmatch(r"[A-Z0-9]{5}", dog_ID))

@app.route('/')
def home():
    return render_template('home.html')
    

@app.route("/employee")
def employee_page():
    name = request.args.get("name", "")
    sex = request.args.get("sex", "Any")
    age = request.args.get("age", "Any")
    selected_breeds = request.args.getlist("breed")
    remove_mode = request.args.get("remove", "false")
    
    
    
    with sqlite3.connect("available_dogs.db") as conn:

        where = []
        params = []

        if name:
            where.append("name LIKE ?")
            params.append(f"%{name}%")

        if selected_breeds:
            placeholders = ",".join(["?"] * len(selected_breeds))
            where.append(f"breed IN ({placeholders})")
            params.extend(selected_breeds)


        order_by = []

        # Sex sorting
        if sex == "Male":
            order_by.append("CASE WHEN sex = 'Male' THEN 0 ELSE 1 END")

        elif sex == "Female":
            order_by.append("CASE WHEN sex = 'Female' THEN 0 ELSE 1 END")


        # Age sorting
        if age == "Youngest":
            order_by.append("age_years ASC")
            order_by.append("age_months ASC")

        elif age == "Oldest":
            order_by.append("age_years DESC")
            order_by.append("age_months DESC")


        order_by.append("name ASC")


        query = "SELECT * FROM available_dogs"

        if where:
            query += " WHERE " + " AND ".join(where)

        query += f" ORDER BY {', '.join(order_by)}"


        dogs_df = pd.read_sql(
            query,
            con=conn,
            params=params
        )
        breed_df = pd.read_sql(
            "SELECT DISTINCT breed FROM available_dogs ORDER BY breed",
            con=conn
        )

        breed_list = breed_df["breed"].tolist()
        
    
            
    # Convert to list of dictionaries for template
    dict_of_dogs = dogs_df.to_dict('records')
        
    for dog in dict_of_dogs:
        dog["age"] = format_age(dog["age_years"], dog["age_months"])
            
    return render_template('employee_portal.html', dogs_list=dict_of_dogs, name=name, breed_list=breed_list, selected_breeds=selected_breeds, sex=sex, age=age, remove_mode=remove_mode)

@app.route("/employee/search")
def search_dogs():
    name = request.args.get("name", "")
    sex = request.args.get("sex", "Any")
    age = request.args.get("age", "Any")
    selected_breeds = request.args.getlist("breed")
    remove_mode = request.args.get("remove", "false")

    with sqlite3.connect("available_dogs.db") as conn:
        where = []
        params = []

        if name:
            where.append("name LIKE ?")
            params.append(f"%{name}%")
        if selected_breeds:
            placeholders = ",".join(["?"] * len(selected_breeds))
            where.append(f"breed IN ({placeholders})")
            params.extend(selected_breeds)


        order_by = []
        
        # Sex sorting
        if sex == "Male":
            order_by.append("CASE WHEN sex = 'Male' THEN 0 ELSE 1 END")
            
        elif sex == "Female":
            order_by.append("CASE WHEN sex = 'Female' THEN 0 ELSE 1 END")
            
        
        # Age sorting
        if age == "Youngest":
            order_by.append("age_years ASC")
            order_by.append("age_months ASC")
        
        elif age == "Oldest":
            order_by.append("age_years DESC")
            order_by.append("age_months DESC")
        
        
        # Default sorting
        
        order_by.append("name ASC")
        
        query = "SELECT * FROM available_dogs"

        if where:
            query += " WHERE " + " AND ".join(where)

        query += f" ORDER BY {', '.join(order_by)}"
        
        
        dogs_df = pd.read_sql(
            query,
            con=conn,
            params=(params)
        )
    dogs_list = dogs_df.to_dict("records")

    for dog in dogs_list:
        dog["age"] = format_age(dog["age_years"], dog["age_months"])

    return render_template("dog_rows.html", dogs_list=dogs_list, remove_mode=remove_mode)


@app.route("/employee/add-a-dog", methods=["GET", "POST"])
def add_a_dog():
    dog_ID = generate_ID()

    if(request.method == "POST"):
        errors = []
        image = request.files["image"]
        if image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = "default.png"
            
        

        name = (request.form["name"].strip())
        if len(name) > 50:
            errors.append("name")
        elif not re.fullmatch(r"[A-Za-z0-9 /'\-]+", name):
            errors.append("name")

        age_years = request.form["age_years"].strip()
        age_months = request.form["age_months"].strip()



        breed = format_word(request.form["breed"].strip())
        if len(breed) > 50:
            errors.append("breed")
        elif not re.fullmatch(r"[A-Za-z0-9 /'\-]+", breed):
            errors.append("breed")

        sex = request.form["sex"].strip()
        if sex not in ["Male", "Female"]:
            errors.append("sex")

        color = format_word(request.form["color"].strip())
        if len(color) > 50:
            errors.append("color")
        elif not re.fullmatch(r"[A-Za-z /-]+", color):
            errors.append("color")

        size = request.form["size"].strip()
        if size not in ["Small", "Medium", "Large"]:
            errors.append("size")

        energy = format_word(request.form["energy"].strip())
        if len(energy) > 300:
            errors.append("energy")
        elif not re.fullmatch(r"[A-Za-z /-]+", energy):
            errors.append("energy")

        personality = format_word(request.form["personality"].strip())
        if len(personality) > 300:
            errors.append("personality")
        elif not re.fullmatch(r"[A-Za-z ,.;:?!&\"\'/-]+", personality):
            errors.append("personality")

        house_trained = request.form["house_trained"].strip()
        if house_trained not in ["Yes", "No"]:
            errors.append("house_trained")

        minimum_child_age = format_word(request.form["minimum_child_age"].strip())
        if minimum_child_age not in ["Not required", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
            errors.append("minimum_child_age")

        good_with_dogs = format_word(request.form["good_with_dogs"].strip())
        if len(good_with_dogs) > 100:
            errors.append("good_with_dogs")
        elif not re.fullmatch(r"[A-Za-z ,.;:?!&\"\'/-]+", good_with_dogs):
            errors.append("good_with_dogs")

        good_with_cats = format_word(request.form["good_with_cats"].strip())
        if len(good_with_cats) > 100:
            errors.append("good_with_cats")
        elif not re.fullmatch(r"[A-Za-z /-]+", good_with_cats):
            errors.append("good_with_cats")

        medical_notes = request.form["medical_notes"].strip()

        adoption_fee = request.form["adoption_fee"].strip()

        adoption_status = request.form["adoption_status"].strip()

        dog = {
            "ID": dog_ID,
            "image": filename,
            "name": name,
            "age_years": age_years,
            "age_months": age_months,
            "breed": breed,
            "sex": sex,
            "color": color,
            "size": size,
            "energy": energy,
            "personality": personality,
            "house_trained": house_trained,
            "minimum_child_age": minimum_child_age,
            "good_with_dogs": good_with_dogs,
            "good_with_cats": good_with_cats,
            "medical_notes": medical_notes,
            "adoption_fee": adoption_fee,
            "adoption_status": adoption_status
        }
        

        if(len(errors) > 0):
            return render_template("dog_profile_editor.html", dog=dog, errors=errors, start_color="red"
        )

        with sqlite3.connect("available_dogs.db") as conn:
            conn.execute(
                """
                INSERT INTO available_dogs
                (
                    ID,
                    image,
                    name,
                    age_years,
                    age_months,
                    breed,
                    sex,
                    color,
                    size,
                    energy,
                    personality,
                    house_trained,
                    minimum_child_age,
                    good_with_dogs,
                    good_with_cats,
                    medical_notes,
                    adoption_fee,
                    adoption_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dog_ID,
                    filename,
                    name,
                    age_years,
                    age_months,
                    breed,
                    sex,
                    color,
                    size,
                    energy,
                    personality,
                    house_trained,
                    minimum_child_age,
                    good_with_dogs,
                    good_with_cats,
                    medical_notes,
                    adoption_fee,
                    adoption_status

                )
            )

            conn.commit()

            return redirect(f"/employee/{dog_ID}?saved=true")


    
    
    dog = {
        "name": "",
        "image": "default.png",
        "age_years": 0,
        "age_months": 0,
        "breed": "",
        "sex": "",
        "color": "",
        "size": "",
        "energy": "",
        "personality": "",
        "house_trained": "",
        "minimum_child_age": "Not required",
        "good_with_dogs": "",
        "good_with_cats": "",
        "medical_notes": "",
        "adoption_fee": "",
        "adoption_status": ""
    }

    
    

    return render_template("dog_profile_editor.html", dog=dog, errors=[], start_color="#50ada3"
)

@app.route("/employee/delete/<dog_ID>", methods=["POST"])
def delete_dog(dog_ID):
    if not valid_dog_id(dog_ID):
        return "Invalid dog ID", 400

    with sqlite3.connect("available_dogs.db") as conn:
        # Optional: get image name so you can delete the file too
        dog = conn.execute(
            "SELECT image FROM available_dogs WHERE ID = ?",
            (dog_ID,)
        ).fetchone()

        conn.execute(
            "DELETE FROM available_dogs WHERE ID = ?",
            (dog_ID,)
        )

        conn.commit()

    # Optional: remove image file from static/images
    if dog and dog[0] != "default.png":
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], dog[0])
        if os.path.exists(image_path):
            os.remove(image_path)

    return redirect("/employee")
    
@app.route("/adopt-a-dog")
def adopt_a_dog():
    name = request.args.get("name", "")
    sex = request.args.get("sex", "Any")
    age = request.args.get("age", "Any")
    selected_breeds = request.args.getlist("breed")
    
        
        
        
    with sqlite3.connect("available_dogs.db") as conn:
    
            where = []
            params = []
    
            if name:
                where.append("name LIKE ?")
                params.append(f"%{name}%")
    
            if selected_breeds:
                placeholders = ",".join(["?"] * len(selected_breeds))
                where.append(f"breed IN ({placeholders})")
                params.extend(selected_breeds)
    
    
            order_by = []
    
            # Sex sorting
            if sex == "Male":
                order_by.append("CASE WHEN sex = 'Male' THEN 0 ELSE 1 END")
    
            elif sex == "Female":
                order_by.append("CASE WHEN sex = 'Female' THEN 0 ELSE 1 END")
    
    
            # Age sorting
            if age == "Youngest":
                order_by.append("age_years ASC")
                order_by.append("age_months ASC")
    
            elif age == "Oldest":
                order_by.append("age_years DESC")
                order_by.append("age_months DESC")
    
    
            order_by.append("name ASC")
    
    
            query = "SELECT * FROM available_dogs"
    
            if where:
                query += " WHERE " + " AND ".join(where)
    
            query += f" ORDER BY {', '.join(order_by)}"
    
    
            dogs_df = pd.read_sql(
                query,
                con=conn,
                params=params
            )
            breed_df = pd.read_sql(
                "SELECT DISTINCT breed FROM available_dogs ORDER BY breed",
                con=conn
            )
    
            breed_list = breed_df["breed"].tolist()
            
        
                
    # Convert to list of dictionaries for template
    dict_of_dogs = dogs_df.to_dict('records')
            
    for dog in dict_of_dogs:
        dog["age"] = format_age(dog["age_years"], dog["age_months"])
                
    return render_template('adopters_page.html', dogs_list=dict_of_dogs, name=name, breed_list=breed_list, selected_breeds=selected_breeds, sex=sex, age=age, )
    
    

@app.route("/adopt-a-dog/search")
def adopter_search_dogs():
    name = request.args.get("name", "")
    sex = request.args.get("sex", "Any")
    age = request.args.get("age", "Any")
    selected_breeds = request.args.getlist("breed")
    

    with sqlite3.connect("available_dogs.db") as conn:
        where = []
        params = []

        if name:
            where.append("name LIKE ?")
            params.append(f"%{name}%")
        if selected_breeds:
            placeholders = ",".join(["?"] * len(selected_breeds))
            where.append(f"breed IN ({placeholders})")
            params.extend(selected_breeds)


        order_by = []
        
        # Sex sorting
        if sex == "Male":
            order_by.append("CASE WHEN sex = 'Male' THEN 0 ELSE 1 END")
            
        elif sex == "Female":
            order_by.append("CASE WHEN sex = 'Female' THEN 0 ELSE 1 END")
            
        
        # Age sorting
        if age == "Youngest":
            order_by.append("age_years ASC")
            order_by.append("age_months ASC")
        
        elif age == "Oldest":
            order_by.append("age_years DESC")
            order_by.append("age_months DESC")
        
        
        # Default sorting
        
        order_by.append("name ASC")
        
        query = "SELECT * FROM available_dogs"

        if where:
            query += " WHERE " + " AND ".join(where)

        query += f" ORDER BY {', '.join(order_by)}"
        
        
        dogs_df = pd.read_sql(
            query,
            con=conn,
            params=(params)
        )
    dogs_list = dogs_df.to_dict("records")

    for dog in dogs_list:
        dog["age"] = format_age(dog["age_years"], dog["age_months"])

    return render_template("adopters_page_rows.html", dogs_list=dogs_list)



@app.route("/employee/<dog_ID>", methods=["GET", "POST"])
def dog_profile_editor(dog_ID):
    if not valid_dog_id(dog_ID):
        return "Invalid dog ID", 400


    if(request.method == "POST"):

        with sqlite3.connect("available_dogs.db") as conn:
            dog = pd.read_sql(
            "SELECT * FROM available_dogs WHERE ID = ?",
            con=conn,
            params=(dog_ID,)
            ).iloc[0].to_dict()
        errors = []
        image = request.files.get("image")

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = dog["image"]

        name = (request.form["name"].strip())
        if len(name) > 50:
            errors.append("name")
        elif not re.fullmatch(r"[A-Za-z0-9 /'\-]+", name):
            errors.append("name")

        age_years = request.form["age_years"].strip()
        age_months = request.form["age_months"].strip()



        breed = format_word(request.form["breed"].strip())
        if len(breed) > 50:
            errors.append("breed")
        elif not re.fullmatch(r"[A-Za-z0-9 /'\-]+", breed):
            errors.append("breed")

        sex = request.form["sex"].strip()
        if sex not in ["Male", "Female"]:
            errors.append("sex")

        color = format_word(request.form["color"].strip())
        if len(color) > 50:
            errors.append("color")
        elif not re.fullmatch(r"[A-Za-z /-]+", color):
            errors.append("color")

        size = request.form["size"].strip()
        if size not in ["Small", "Medium", "Large"]:
            errors.append("size")

        energy = format_word(request.form["energy"].strip())
        if len(energy) > 300:
            errors.append("energy")
        elif not re.fullmatch(r"[A-Za-z /-]+", energy):
            errors.append("energy")

        personality = format_word(request.form["personality"].strip())
        if len(personality) > 300:
            errors.append("personality")
        elif not re.fullmatch(r"[A-Za-z /-]+", personality):
            errors.append("personality")

        house_trained = request.form["house_trained"].strip()
        if house_trained not in ["Yes", "No"]:
            errors.append("house_trained")

        minimum_child_age = format_word(request.form["minimum_child_age"].strip())
        if minimum_child_age not in ["Not required", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
            errors.append("minimum_child_age")

        good_with_dogs = format_word(request.form["good_with_dogs"].strip())
        if len(good_with_dogs) > 100:
            errors.append("good_with_dogs")
        elif not re.fullmatch(r"[A-Za-z /-]+", good_with_dogs):
            errors.append("good_with_dogs")

        good_with_cats = format_word(request.form["good_with_cats"].strip())
        if len(good_with_cats) > 100:
            errors.append("good_with_cats")
        elif not re.fullmatch(r"[A-Za-z /-]+", good_with_cats):
            errors.append("good_with_cats")

        medical_notes = request.form["medical_notes"].strip()

        adoption_fee = request.form["adoption_fee"].strip()

        adoption_status = request.form["adoption_status"].strip()

        
        
        dog["age"] = format_age(dog["age_years"], dog["age_months"])
        dog["image"] = image
        dog["name"] = name
        dog["age_years"] = age_years
        dog["age_months"] = age_months
        dog["breed"] = breed
        dog["sex"] = sex
        dog["color"] = color
        dog["size"] = size
        dog["energy"] = energy
        dog["personality"] = personality
        dog["house_trained"] = house_trained
        dog["minimum_child_age"] = minimum_child_age
        dog["good_with_dogs"] = good_with_dogs
        dog["good_with_cats"] = good_with_cats
        dog["medical_notes"] = medical_notes
        dog["adoption_fee"] = adoption_fee
        dog["adoption_status"] = adoption_status

        if(len(errors) > 0):
            return render_template("dog_profile_editor.html", dog=dog, errors=errors, start_color="red"
        )

        with sqlite3.connect("available_dogs.db") as conn:
            conn.execute(
                """
                UPDATE available_dogs
                SET 
                    name=?, 
                    image=?,
                    age_years=?,
                    age_months=?, 
                    breed=?, 
                    sex=?, 
                    color=?, 
                    size=?,
                    energy=?,
                    personality=?,
                    house_trained=?,
                    minimum_child_age=?,
                    good_with_dogs=?,
                    good_with_cats=?,
                    medical_notes=?,
                    adoption_fee=?,
                    adoption_status=?
                WHERE ID=?
                """,
                (name,filename,age_years,age_months,breed,sex,color,size,energy,personality,house_trained,minimum_child_age,
                 good_with_dogs,good_with_cats,medical_notes,adoption_fee,adoption_status,dog_ID)
            )

            conn.commit()

            return redirect(f"/employee/{dog_ID}?saved=true")


    
    


    with sqlite3.connect("available_dogs.db") as conn:
        dog = pd.read_sql(
            "SELECT * FROM available_dogs WHERE ID = ?",
            con=conn,
            params=(dog_ID,)
        ).iloc[0].to_dict()

    

    saved = request.args.get("saved")

    if saved == "true":
        start_color = "#28a745"
    elif saved == "false":
        start_color = "#C12626"
    else:
        start_color = "#50ada3"

    return render_template("dog_profile_editor.html", dog=dog, errors=[], start_color=start_color
)
    

if __name__ == '__main__':
    
    app.run(debug=True)