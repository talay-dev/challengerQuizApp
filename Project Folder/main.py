# Import necessary libraries
import pyfiglet
import os
import time
import sqlite3 as sql
import hashlib
import matplotlib.pyplot as plt


"""
users and passwords: 
    omer = kaplan
    aliugur = lord
    veysi = kaya
    yunus = aslan
    mustafa = cengaver
    kahya = dolap
"""


# Function to clear the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to get a valid username from the user


def get_username():
    while True:
        username = input("Enter your username (at least 3 characters): ")
        if len(username) >= 3:
            return username
        print("Username must be at least 3 characters long.")

# Function to get a valid password from the user


def get_password():
    while True:
        password = input("Enter your password (at least 4 characters): ")
        if len(password) >= 4:
            return password
        print("Password must be at least 4 characters long.")

# Function to hash the password using SHA256


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to register a new user


def register():
    print("Welcome to the register page")
    username = get_username()
    password = get_password()
    hashed_password = hash_password(password)

    # Insert the new user into the database
    try:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                        (username, hashed_password))
            con.commit()
            print("You have been registered successfully")
            login()
    except sql.IntegrityError:
        print("Username already exists. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to log in an existing user


def login():
    print("Welcome to the login page")

    while True:
        username = get_username()
        password = get_password()
        hashed_password = hash_password(password)

        # Check if the entered username and password match a user in the database
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                        (username, hashed_password))
            result = cur.fetchone()

            if result:
                clear_screen()
                print("Login successful")
                global current_user
                current_user = username
                main_menu()
                return True
            print("Incorrect username or password. Please try again.")


# Function to display categories and prompt user to select one
def category_selection():
    # List of available categories
    categories = [
        "Science__Computers",
        "General_Knowledge",
        "Entertainment__Music",
        "Entertainment__Television",
        "Entertainment__Video_Games",
        "Science_and_Nature",
        "Geography",
        "History"
    ]

    # Display categories for selection
    print("\nSelect a category:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")

    # Get the user's choice and validate it
    while True:
        choice = input(
            "Enter the number of the category you'd like to select: ")
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        print("Invalid choice. Please enter a valid number.")

# Function to conduct a quiz for the selected category


def quiz_taker(category):
    # Fetch questions from the selected category
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(
            "SELECT question, answer FROM {} ORDER BY RANDOM()".format(category))
        questions = cur.fetchall()

    # Check if there are any questions in the category
    if not questions:
        print("No questions found in this category.")
        return

    # Start the quiz
    print(f"Starting quiz for category: {category}")
    time.sleep(0.5)
    clear_screen()

    correct_answers = 0
    start_time = time.time()

    # Loop through the questions and get user input
    for question, correct_answer in questions:
        print(question)
        user_answer = input("Answer with 't' or 'f': ").lower()
        if user_answer == 't':
            user_answer = 'true'
        elif user_answer == 'f':
            user_answer = 'false'
        else:
            print("Invalid answer. Please enter 't' or 'f'.")
            continue
        if user_answer == correct_answer.lower():
            correct_answers += 1
        time.sleep(0.5)
        clear_screen()

    # Calculate the score and save it in the database
    end_time = time.time()
    elapsed_time = end_time - start_time
    score = correct_answers / elapsed_time * 100

    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO taken_quizzes (username, category, score, points, time) VALUES (?, ?, ?, ?, ?)",
                    (current_user, category, score, correct_answers, elapsed_time))
        con.commit()

    # Display the quiz results
    print(" Quiz Results ".center(40, "="))
    print(f"{'Category:':<20}{category}")
    print(f"{'Points:':<20}{correct_answers}")
    print(f"{'Time:':<20}{elapsed_time:.2f} seconds")
    print(f"{'Score:':<20}{score:.2f}")
    print("".center(40, "="))
    input("Press enter to continue...")
    clear_screen()

# Function to display the statistics menu and handle user selections


def statistics_selection():
    while True:
        clear_screen()
        print("\n" + "Statistics Menu".center(40, "="))
        print("1. Score statistics across all quizzes".center(40))
        print("2. Time statistics across all quizzes".center(40))
        print("3. Number of quizzes taken in each category".center(40))
        print("4. Ranking among users for a specific quiz".center(40))
        print("5. Back to Main Menu".center(40))
        print("".center(40, "="))

        choice = input("Enter the number of your choice: ")
        clear_screen()

        # Handle user selections
        if choice == '1':
            display_score_statistics(current_user)
            input("Press enter to go back")
        elif choice == '2':
            display_time_statistics(current_user)
            input("Press enter to go back")
        elif choice == '3':
            display_quizzes_by_category(current_user)
            input("Press enter to go back")
        elif choice == '4':
            quiz_category = category_selection()
            clear_screen()
            display_ranking(current_user, quiz_category)
            input("Press enter to go back")
        elif choice == '5':
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice. Please enter a valid number.")

# Function to display the score statistics for the current user


def display_score_statistics(current_user):
    # Fetch scores from the database for the current user
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(
            "SELECT score FROM taken_quizzes WHERE username = ?", (current_user,))
        scores = [row[0] for row in cur.fetchall()]

    # Check if there are any quizzes taken by the current user
    if not scores:
        print(f"No quizzes taken by {current_user}.")
        return

    # Calculate average, minimum, and maximum scores
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    max_score = max(scores)

    # Display the score statistics
    print("\n" + f"Score statistics for {current_user}".center(40, "="))
    print(f"Average score:".ljust(25) + f"{avg_score:.2f}".rjust(15))
    print(f"Minimum score:".ljust(25) + f"{min_score:.2f}".rjust(15))
    print(f"Maximum score:".ljust(25) + f"{max_score:.2f}".rjust(15))
    print("".center(40, "="))

    # Add this after calculating avg_score, min_score, and max_score
    labels = ["Average", "Min", "Max"]
    values = [avg_score, min_score, max_score]

    # Plot the score statistics using matplotlib
    plt.bar(labels, values)
    plt.title(f"Score Statistics for {current_user}")
    plt.ylabel("Scores")
    plt.show()


def display_time_statistics(current_user):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute(
            "SELECT time FROM taken_quizzes WHERE username = ?", (current_user,))
        times = [row[0] for row in cur.fetchall()]

        if not times:
            print(f"No quizzes taken by {current_user}.")
            return

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print("\n" + f"Time Statistics for {current_user}".center(40, "="))
        print(f"Average time (seconds):".ljust(
            25) + f"{avg_time:.2f}".rjust(15))
        print(f"Minimum time (seconds):".ljust(
            25) + f"{min_time:.2f}".rjust(15))
        print(f"Maximum time (seconds):".ljust(
            25) + f"{max_time:.2f}".rjust(15))
        print("".center(40, "="))

        # Add this after calculating avg_time, min_time, and max_time
        labels = ["Average", "Min", "Max"]
        values = [avg_time, min_time, max_time]

        plt.bar(labels, values)
        plt.title(f"Time Statistics for {current_user}")
        plt.ylabel("Time (seconds)")
        plt.show()


def display_quizzes_by_category(current_user):
    categories = [
        "Science__Computers",
        "General_Knowledge",
        "Entertainment__Music",
        "Entertainment__Television",
        "Entertainment__Video_Games",
        "Science_and_Nature",
        "Geography",
        "History"
    ]

    with sql.connect("database.db") as con:
        cur = con.cursor()

        print(
            "\n" + f"Taken quizzes by Category for {current_user}".center(50, "="))

        for category in categories:
            cur.execute(
                "SELECT COUNT(*) FROM taken_quizzes WHERE username = ? AND category = ?", (current_user, category))
            count = cur.fetchone()[0]
            print(f"{category.replace('_', ' '):<35}: {count:>13}")

        print("".center(50, "="))

    # Add this after fetching the count for each category
    counts = []
    for category in categories:
        cur.execute(
            "SELECT COUNT(*) FROM taken_quizzes WHERE username = ? AND category = ?", (current_user, category))
        count = cur.fetchone()[0]
        counts.append(count)

    plt.bar(categories, counts)
    plt.title(f"Quizzes by Category for {current_user}")
    plt.xlabel("Categories")
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Number of quizzes")
    plt.show()


def display_ranking(current_user, category):
    with sql.connect("database.db") as con:
        cur = con.cursor()

        # Fetch highest scores for each user in the given category
        cur.execute(
            "SELECT username, MAX(score) as max_score FROM taken_quizzes WHERE category = ? GROUP BY username", (category,))
        user_scores = cur.fetchall()

        # Sort users by highest score in descending order
        user_scores.sort(key=lambda x: x[1], reverse=True)

        # Find the current user's ranking
        rank = 1
        for user, score in user_scores:
            if user == current_user:
                break
            rank += 1

        # Print ranking information
        print(
            "\n" + f"Ranking for {current_user} in {category}".center(40, "="))
        print(f"Your rank: {rank} out of {len(user_scores)}")

        # Write all users in ranking order with 2 decimal places
        rank = 1
        for user, score in user_scores:
            print(f"{rank}. {user:<20}: {score:.2f}")
            rank += 1
        print("".center(40, "="))

        # Plot bar chart of users' highest scores in the given category
        usernames = [user for user, score in user_scores]
        max_scores = [score for user, score in user_scores]

        plt.bar(usernames, max_scores)
        plt.title(f"Highest Scores by User in {category}")
        plt.xlabel("Users")
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Highest Scores")
        plt.show()


def main_menu():
    while True:
        clear_screen()
        print("\n" + " Main Menu ".center(40, "="))
        print("1. Take quiz".center(40))
        print("2. Statistics".center(40))
        print("3. Exit".center(40))
        print("".center(40, "="))

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            category = category_selection()
            clear_screen()
            print(f"Category: {category}")
            print("Quiz starting in 3 seconds...")
            time.sleep(3)
            clear_screen()
            quiz_taker(category)

        elif choice == '2':
            statistics_selection()

        elif choice == '3':
            clear_screen()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid number.")


def main():

    while True:
        choice = input("Enter 'r' to register or 'l' to login: ")
        if choice.lower() == 'r':
            register()
            break

        elif choice.lower() == 'l':
            if login():
                break
        else:
            print("Invalid choice. Please enter 'r' or 'l'.")


if __name__ == "__main__":
    pyfiglet.print_figlet("Challenger")
    main()
