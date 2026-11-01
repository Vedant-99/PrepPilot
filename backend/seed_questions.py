from database import get_connection,init_db

# Each question is one line:(category, topic, difficulty, question, key_points)
# key_points = what a good answer should cover (plain text, written by us)
QUESTIONS = [
    # ---------- Technical ----------
    ("technical", "Python", "easy",
     "What is the difference between a list and a tuple in Python?",
     "List can change (mutable), tuple cannot (immutable); tuple can be a dictionary key; use tuple for fixed data, list for data that changes."),
    ("technical", "OOP", "easy",
     "What are the four pillars of OOP?",
     "Encapsulation (data and methods together), abstraction (hide details), inheritance (reuse a parent class), polymorphism (same method, different behaviour); give one small example."),
    ("technical", "SQL", "medium",
     "What is the difference between INNER JOIN and LEFT JOIN?",
     "INNER JOIN gives only rows that match in both tables; LEFT JOIN gives all rows of the left table and NULL where there is no match; example: users and orders."),
    ("technical", "Web", "easy",
     "What is the difference between GET and POST in HTTP?",
     "GET reads data and puts values in the URL; POST sends data in the body to create or change something; never send passwords in a URL."),
    ("technical", "Databases", "medium",
     "What is a primary key and what is a foreign key?",
     "Primary key identifies each row, so no duplicates and no NULL; foreign key points to the primary key of another table and links the tables; example: user_id in profiles."),

    # ---------- DSA ----------
    ("dsa", "Arrays", "easy",
     "What is the time complexity of searching in an unsorted array, and how can you make it faster?",
     "Checking one by one is O(n); sort first and use binary search O(log n); or use a hash set for fast lookup on average O(1)."),
    ("dsa", "Stack and Queue", "easy",
     "What is the difference between a stack and a queue?",
     "Stack is LIFO (last in, first out), queue is FIFO (first in, first out); stack example: undo button; queue example: line at a ticket counter."),
    ("dsa", "Searching", "medium",
     "Explain how binary search works.",
     "Array must be sorted; compare with the middle element; throw away the half that cannot have the answer; repeat; time is O(log n)."),
    ("dsa", "Hash Map", "medium",
     "How does a hash map work and what is a collision?",
     "Key goes through a hash function to get an index; lookup is O(1) on average; collision means two keys get the same index; fixed with chaining or open addressing."),
    ("dsa", "Linked List", "medium",
     "How would you detect a cycle in a linked list?",
     "Use two pointers, slow moves 1 step and fast moves 2 steps; if they meet there is a cycle; O(n) time and O(1) extra space; a visited set also works but uses more memory."),

    # ---------- HR ----------
    ("hr", "Introduction", "easy",
     "Tell me about yourself.",
     "Keep it about one minute: name, course, what you built, skills for this role, why you want this role; talk only about real projects."),
    ("hr", "Self awareness", "easy",
     "What is your biggest weakness?",
     "Pick a real and small weakness; say what you are doing to improve; give a short example; avoid fake answers like I work too hard."),
    ("hr", "Teamwork", "medium",
     "Tell me about a time you worked in a team and faced a problem.",
     "Use STAR: Situation, Task, Action, Result; say what YOU did, not only the team; end with what you learned."),
    ("hr", "Motivation", "easy",
     "Why do you want to join our company?",
     "Research the company before; connect their work to your skills; be honest; do not say only salary."),
    ("hr", "Failure", "medium",
     "Tell me about a time you failed.",
     "Use STAR; own the mistake and do not blame others; explain what you changed after it."),

      # ---------- More Technical (hard) ----------
    ("technical", "Python", "hard",
     "What is the GIL in Python and how does it affect multithreading?",
     "GIL lets only one thread run Python code at a time; threads do not speed up heavy CPU work; threads are still fine when the program waits for files or network; use multiprocessing for CPU-heavy work."),
    ("technical", "Databases", "hard",
     "What is a database index and what is the cost of adding too many indexes?",
     "Index works like the index of a book: finds rows fast without reading the whole table; usually built as a B-tree; makes INSERT, UPDATE and DELETE slower and uses extra space; index columns used in WHERE and JOIN."),
    ("technical", "Web", "hard",
     "What is the difference between authentication and authorization, and how does a session cookie work?",
     "Authentication = who are you; authorization = what are you allowed to do; after login the server saves a session and sends a cookie; browser sends the cookie with every request; passwords must be hashed, never saved as plain text."),
    ("technical", "Databases", "hard",
     "What is database normalization? Explain 1NF, 2NF and 3NF in simple words.",
     "Normalization removes repeated data by splitting tables; 1NF: one value in each cell; 2NF: every column depends on the whole key; 3NF: columns do not depend on other non-key columns; trade-off: more joins."),

     # ---------- More DSA (hard) ----------
    ("dsa", "Strings", "hard",
     "How would you find the longest substring without repeating characters?",
     "Use the sliding window with two pointers; keep the characters of the window in a set; when a repeat comes, move the left pointer forward; remember the longest window; O(n) time."),
    ("dsa", "Sorting", "hard",
     "Explain how merge sort works and why its time is O(n log n).",
     "Split the array into halves until each has 1 element; merge the sorted halves back; there are log n levels and each level does O(n) work; needs O(n) extra space; it is stable."),
    ("dsa", "Graphs", "hard",
     "What is the difference between BFS and DFS, and when would you use each?",
     "BFS uses a queue and goes level by level, so it finds the shortest path in an unweighted graph; DFS uses a stack or recursion and goes deep first, good for cycle detection and checking paths; both take O(V+E)."),
    ("dsa", "Dynamic Programming", "hard",
     "What is dynamic programming? Explain it with the Fibonacci example.",
     "Break a problem into small repeated subproblems and save their answers; plain recursion for Fibonacci repeats work and takes O(2^n); memoization or a table makes it O(n); two ways: top-down and bottom-up."),

     # ---------- More HR ----------
    ("hr", "Goals", "medium",
     "Where do you see yourself in five years?",
     "Give a realistic and honest goal; talk about learning and growing in this role; connect it to the company; do not say you will leave soon."),
    ("hr", "Selling yourself", "hard",
     "Why should we hire you over other candidates?",
     "Match your skills to the job; give one proof, like a project you built; show you learn fast; never put other candidates down."),
    ("hr", "Conflict", "hard",
     "Tell me about a disagreement with a teammate and how you solved it.",
     "Use STAR; stay calm and listen to their side; talk about the problem, not the person; say what you did and what the result was."),
    ("hr", "Pressure", "medium",
     "How do you handle pressure or a tight deadline?",
     "Use STAR with a real example like an exam or project deadline; plan and set priorities; ask for help early; say what you learned."),


]

def seed_questions():
    # Make sure tables exists before we add data
    init_db()
    conn = get_connection()

    # Insert/Ignore skips a question that is already saved(question is UNIQUE)
    # The ? marks are filled safely from each line of questions

    conn.executemany(
        """
        INSERT OR IGNORE INTO questions (category, topic, difficulty,question, key_points)
        VALUES(?,?,?,?,?)
        """,
        QUESTIONS,
    )
    conn.commit()

    # Count how many questions are saved now
    total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    conn.close()
    print(f"Question bank ready:{total} questions")
          
# Runs only when you start this file directory
if __name__ == "__main__":
    seed_questions()
