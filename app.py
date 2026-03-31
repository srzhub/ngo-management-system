from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import get_connection

app = Flask(__name__)
app.secret_key = "your_secret_key"  

@app.route("/")
def home():
    return redirect(url_for("view_donations"))

# Add Donation (with donor FK logic)

@app.route("/add_donation", methods=["GET", "POST"])
def add_donation():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    # POST : Add donation
    if request.method == "POST":
        # 1. Handle new donor creation
        new_name  = request.form.get("new_donor_name", "").strip()
        new_email = request.form.get("new_donor_email", "").strip() or None
        new_phone = request.form.get("new_donor_phone", "").strip() or None
        donor_id  = request.form.get("donor_id") or None

        if new_name:
            cur.execute(
                "INSERT INTO donors (name, email, phone) VALUES (%s, %s, %s)",
                (new_name, new_email, new_phone)
            )
            donor_id = cur.lastrowid

        # 2. Read donation fields
        campaign_id = request.form.get("campaign_id") or None
        amount      = request.form["amount"]
        date        = request.form["date"]
        dtype       = request.form["type"]

        # 3. Insert donation
        cur.execute("""
            INSERT INTO donations (donor_id, campaign_id, amount, date, type)
            VALUES (%s, %s, %s, %s, %s)
        """, (donor_id, campaign_id, amount, date, dtype))
        conn.commit()

        cur.close()
        conn.close()

        flash("Donation recorded successfully!", "success")
        return redirect(url_for("view_donations"))

    # GET: load dropdown data
    cur.execute("SELECT id, name FROM donors ORDER BY name")
    donors = cur.fetchall()
    cur.execute("SELECT id, name FROM campaigns ORDER BY name")
    campaigns = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("add_donation.html", donors=donors, campaigns=campaigns)


# Add Volunteer
 
@app.route("/add_volunteer", methods=["GET", "POST"])
def add_volunteer():
    if request.method == "POST":
        name  = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO volunteers (name, phone, email)
            VALUES (%s, %s, %s)
        """, (name, phone, email))
        conn.commit()
        cur.close()
        conn.close()
        flash("Volunteer registered successfully!", "success")
        return redirect(url_for("view_volunteers"))

    return render_template("add_volunteer.html")


# Add Event

@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        name        = request.form["name"]
        date        = request.form["date"]
        location    = request.form["location"]
        description = request.form["description"]

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO events (name, date, location, description)
            VALUES (%s, %s, %s, %s)
        """, (name, date, location, description))
        conn.commit()
        cur.close()
        conn.close()
        flash("Event added successfully!", "success")
        return redirect(url_for("view_events"))

    return render_template("add_event.html")


# Add Campaign

@app.route("/add_campaign", methods=["GET", "POST"])
def add_campaign():
    if request.method == "POST":
        name             = request.form["name"]
        goal_amount      = request.form["goal_amount"]
        collected_amount = request.form["collected_amount"]

        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO campaigns (name, goal_amount, collected_amount)
            VALUES (%s, %s, %s)
        """, (name, goal_amount, collected_amount))
        conn.commit()
        cur.close()
        conn.close()
        flash("Campaign created successfully!", "success")
        return redirect(url_for("view_campaigns"))

    return render_template("add_campaign.html")


# View Donations

@app.route("/view_donations")
def view_donations():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT d.id, COALESCE(donor.name, '—') AS donor_name,
               c.name AS campaign_name,
               d.amount, d.date, d.type
        FROM donations d
        LEFT JOIN donors donor ON d.donor_id = donor.id
        LEFT JOIN campaigns c  ON d.campaign_id = c.id
        ORDER BY d.id DESC
    """)
    donations = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view_donations.html", donations=donations)


# View Volunteers

@app.route("/view_volunteers")
def view_volunteers():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM volunteers ORDER BY id DESC")
    volunteers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view_volunteers.html", volunteers=volunteers)


# View Events

@app.route("/view_events")
def view_events():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM events ORDER BY date DESC")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view_events.html", events=events)


# View Campaigns

@app.route("/view_campaigns")
def view_campaigns():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM campaigns ORDER BY id DESC")
    campaigns = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view_campaigns.html", campaigns=campaigns)


if __name__ == "__main__":
    app.run(debug=True)
