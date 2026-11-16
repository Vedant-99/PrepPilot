# Skills to look for in a resume, and the words that count as that skill
# Example: if resume has "reactjs", the skill "React" is found

SKILL_ALIASES = {
    "HTML" : ["html","html5"],
    "CSS"  : ["css","css3"],
    "JavaScript": ["javascript","js","es6"],
    "TypeScript": ["typescript"],
    "React" : ["react","reactjs","react.js"],
    "Node.js" : ["node.js","nodejs","node js"],
    "Python" : ["python","py"],
    "Java" : ["java"],
    "C++" : ["c++"],
    "SQL" : ["sql","mysql","postgresql","sqlite"],
    "MongoDB" : ["mongodb","mongo"],
    "Git" : ["git","github"],
    "Docker" : ["docker"],
    "AWS" : ["aws", "amazon web services"],
    "Linux" : ["linux"],
    "REST APIs" : ["rest api", "rest apis", "restful"],
    "DSA" : ["dsa","data structures","algorithms"],
    "OOP" : ["oop","object-oriented","object-oriented"],
    "DBMS" : ["dbms","database management"],
    "Pandas" : ["pandas"],
    "Excel" : ["excel"],
    "Power BI" : ["power bi","powerbi"],
    "Statistics" : ["statistics","statistical"],
    "Data Visualization" : ["data visualization", "tableau","matplotlib"],
}

#  Which skills each target role needs
#  The role names are the same as the dropdown on the profile page

ROLE_SKILLS = {
    "Frontend Developer" : ["HTML", "CSS", "JavaScript", "TypeScript", "React","REST APIs" , "Git"],
    "Backend Developer"  : ["Python", "Java", "Node.js","SQL", "REST APIs","DBMS","Git","Docker"],
    "Full Stack Developer" : ["HTML", "CSS", "JavaScript", "React", "Node.js","SQL", "MongoDB","REST APIs","Git"],
    "Software Engineer" : ["DSA","OOP","DBMS","SQL","Python","Java","Git","Linux"],
    "Data Analyst" : ["SQL","Python","Pandas","Excel","Power BI", "Statistics","Data Visualization"],
}


# Runs only when you start this file directly
#  A quick check: every skill in a role must also exits in SKILL_ALIASES

if __name__ == "__main__":
    for role, skills in ROLE_SKILLS.items():
        missing = [skill for skill in skills if skill not in SKILL_ALIASES]
        print(f"{role}: {len(skills)} skills, missing from aliases: {missing}")