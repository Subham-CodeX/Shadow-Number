from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# In-memory leaderboard
leaderboard = []

def generate_secret():
    digits = list("0123456789")
    random.shuffle(digits)
    return "".join(digits[:4])

def calculate_feedback(secret, guess):
    fames, dots = [], []
    for i, digit in enumerate(guess):
        if digit == secret[i]:
            fames.append((digit, i))
        elif digit in secret:
            dots.append((digit, i))
    return fames, dots

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_name = request.form.get("player_name") or "Anonymous"
        avatar = request.form.get("avatar") or "🙂"
        session["player_name"] = player_name
        session["avatar"] = avatar
        session["secret"] = generate_secret()
        session["attempts"] = []
        return redirect(url_for("game"))
    return render_template("index.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    secret = session.get("secret")
    attempts = session.get("attempts", [])

    if request.method == "POST":
        guess = request.form.get("guess")
        if len(guess) == 4 and guess.isdigit() and len(set(guess)) == 4:
            fames, dots = calculate_feedback(secret, guess)
            attempts.append({"guess": guess, "fames": fames, "dots": dots})
            session["attempts"] = attempts
            if len(fames) == 4:
                return redirect(url_for("result"))
    return render_template("game.html", attempts=attempts)

@app.route("/result")
def result():
    secret = session.get("secret")
    attempts = session.get("attempts", [])
    player_name = session.get("player_name", "Anonymous")
    avatar = session.get("avatar", "🙂")
    attempt_count = len(attempts)

    # Personal best score
    best_score = session.get("best_score")
    if best_score is None or attempt_count < best_score:
        session["best_score"] = attempt_count
        best_score = attempt_count

    # Update leaderboard
    leaderboard.append({"name": player_name, "avatar": avatar, "score": attempt_count})
    leaderboard.sort(key=lambda x: x["score"])
    top_leaderboard = leaderboard[:5]

    return render_template("result.html",
                           secret=secret,
                           attempts=attempts,
                           attempt_count=attempt_count,
                           best_score=best_score,
                           leaderboard=top_leaderboard)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
