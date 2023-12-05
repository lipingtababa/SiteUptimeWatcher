# Overview
This is a coding assignmentfor a backend developer position at Aiven.
Homework evaluation is one ofthe criteria we use when selecting the candidates for the interview, so pay attention that your solution demonstrates your skills in developing production quality code.

# Language Requirements
Please use Python forthe exercise, otherwise, you have the freedom to select
suitable tools and libraries (with a few exceptions listed below), but make sure the work demonstrates well your own coding skills.

# Use Scenaria
The implementation is discussed as one topic during the technical interview.
You will be given access to a private repository on GitHub where you should push your solution;to return your homework, store the code and related documentation on such repository for easy access;then, notify your Aiven contactthat you're done.

# Copyright
If you ran out of time and you are returning a partial solution, describe whatis missing and how you would continue.
Your code will only be used forthe evaluation, and you’re free to use it as you like, as you own it. If you wantto publish it publicly e.g. in Github we’d kindly ask you to remove all Aiven references from it.

# Functionality Requirments
Yourtask is to implement a program that monitors the availability of many websites overthe network, produces metrics aboutthese and stores the metrics into an Aiven PostgreSQL database.
The website monitor should perform the checks periodically and collect the request timestamp,the response time,the HTTP status code, as well as **optionally** checking the returned page contents for a regex pattern thatis expected to be found on the page. Each URL should be checked periodically, with the ability to configure the interval(between 5 and 300 seconds) and the regexp on a per-URL basis. The monitored URLs can be anything found online.

# Storage Requirements
Aiven is a Database as a Service vendor and the homework requires using our
services. Please registerto Aiven at https://console.aiven.io/signup at which point you'll automatically be given $300 worth of credits to play around with. The credits should be enough for a few hours of use of our services. If you need more credits to complete your homework, please contact us.

# Don'ts
The solution should NOT include using any ofthe following:
- Database ORM libraries - use a Python DB API or similarlibrary and raw SQL
queries instead.

- External Scheduling libraries - we really wantto see yourtake on concurrency.

- Extensive container build recipes - ratherfocus your effort on the Python code, tests, documentation, etc.

#  Criteria for Evaluation
- Please keep the code simple and understandable. Anything unnecessarily
complex, undocumented or untestable will be considered a minus.


- Main design goal is maintainability.
- The solution
    - Must work (we need to be able to run the solution)
    - Must be tested and have tests
    - Must handle errors.
    - Should be production quality.
    - Should work for at least some thousands of separate sites (no need to provide proof ofthis).
    - Note! If something is notimplemented in a way that meets these requirements e.g. due to time constraints, explicitly state these shortcomings and explain what would be the correct way of implementing it.

- Code formatting and clarity: “Programs must be written for people to read, and only incidentally for machines to execute.” (Harold Abelson, Structure and
Interpretation of Computer Programs)

- Attribution. If you take code from Google results, examples etc., add attributions. We all know new things are often written based on search results.

- Continuous Integration is not evaluated.

# And More
Attached to this email is a file which includes the assignment and the instructions. Please be attentive to the wording and directions of the assignment. Our team will be looking for clean, production-ready code and inclusion of what you consider to be coding “best practices.”

If you have any questions while working on the assignment, please do not hesitate to get in touch with me. I will consult with the team and get back to you with their answers.

Also, I have sent you an invite to a private Github repo to which you can commit your code. Once your assignment is complete, please push the Github link to the comment section within the link below. If you do not complete this step, we cannot grade your home assignment

The engineering team will review your code and provide feedback. If the results are positive, we will then schedule the Team Interview via Google Meet.

We typically offer 7 days to complete this assignment. If anything comes up and you need more time, just let me know.