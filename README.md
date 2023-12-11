# Assumptions while Designing
* As instructed, the project should be easy to maintain. I will do my best to find the sweet spot between extensibility and readability.
* Extensibility is desired. For example, future support for HTTP Basic Authentication, POST method, or multi-tenancy might be required.
* Scalability is essential. The application will scale out across multiple nodes (e.g., K8S containers, AWS Lambda Functions, AWS Fargate containers), operating independently in parallel.
* The network will be highly heterogeneous. For example, some endpoints might reside in an Intranet [10.0.0.0/8](https://en.wikipedia.org/wiki/Private_network), or more challengingly, in DoD/USA's [11.0.0.0/8](https://news.ycombinator.com/item?id=10006534).
* Cost efficiency is a key competitive factor. We should be able to calculate the unit price per URL monitored and reduce it to the smallest possible while maintaining a decent SLA.
* To reduce complexity and infrastructure cost, it is acceptable to lose a small amount of time-series data.

# Classes Overview
For every node, there is one [Worker](./src/worker.py), which sends HTTP requests to each [Endpoint](./src/endpoint.py) and put the generated [Stat](./src/metrics.py) into a buffer. A proper number of [Keeper](./src/Keeper.py) are provisioned to dump the stats into DB.
All of the tasks run in the same event loop, which means that multiple CPU cores are not utilized at this moment.

# Concurrency 
[asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) have been chosen for concurrency. The configuration that can utilize resources most effectively requires further fine-tuning in the production environments.

# DB Schema
There are 2 tables: the relational **sites** table where urls are managed and **stats** which contains the time series data.

Please note that **URL** shouldn't be a primary key since you can have duplicate URLs in case
- With the same URL, users might specify different regex. 
- If the application is deployed on Intranet, the same url "https://10.0.0.1/index" might point to different endpoints.
- If Aiven provides url-monitoring-as-a-service and 2 users might specify the same URL and Aiven should be able to distinguish them.


# TODO
- Kill the process periodically to stop memory leak or any weird stuff
- Support POST, Basic Auth and other features specific to some sites
- Handle exceptions
- Choose the more performing data structures for StatsBuffer and the Stats list used in Keeper


# Requirements
## Overview
This is a coding assignment for a backend developer position at Aiven.
Homework evaluation is one of the criteria we use when selecting the candidates for the interview, so pay attention that your solution demonstrates your skills in developing production quality code.

## Language Requirements
Please use Python for the exercise, otherwise, you have the freedom to select
suitable tools and libraries (with a few exceptions listed below), but make sure the work demonstrates well your own coding skills.

## Use Scenaria
The implementation is discussed as one topic during the technical interview.
You will be given access to a private repository on GitHub where you should push your solution;to return your homework, store the code and related documentation on such repository for easy access;then, notify your Aiven contactthat you're done.

## Copyright
If you ran out of time and you are returning a partial solution, describe what is missing and how you would continue.
Your code will only be used for the evaluation, and you’re free to use it as you like, as you own it. If you want to publish it publicly e.g. in Github we’d kindly ask you to remove all Aiven references from it.

## Functionality Requirments
Your task is to implement a program that monitors the availability of many websites over the network, produces metrics about these and stores the metrics into an Aiven PostgreSQL database.
The website monitor should perform the checks periodically and collect the request timestamp,the response time, the HTTP status code, as well as **optionally** checking the returned page contents for a regex pattern that is expected to be found on the page. Each URL should be checked periodically, with the ability to configure the interval(between 5 and 300 seconds) and the regexp on a per-URL basis. The monitored URLs can be anything found online.

## Storage Requirements
Aiven is a Database as a Service vendor and the homework requires using our services. Please registerto Aiven at https://console.aiven.io/signup at which point you'll automatically be given $300 worth of credits to play around with. The credits should be enough for a few hours of use of our services. If you need more credits to complete your homework, please contact us.

## Don'ts
The solution should NOT include using any ofthe following:
- Database ORM libraries - use a Python DB API or similarlibrary and raw SQL queries instead.

- External Scheduling libraries - we really want to see your take on concurrency.

- Extensive container build recipes - rather focus your effort on the Python code, tests, documentation, etc.

##  Criteria for Evaluation
- Please keep the code simple and understandable. Anything unnecessarily complex, undocumented or untestable will be considered a minus.
- Main design goal is maintainability.
- The solution
    - Must work (we need to be able to run the solution)
    - Must be tested and have tests
    - Must handle errors.
    - Should be production quality.
    - Should work for at least some thousands of separate sites (no need to provide proof of this).
    - Note! If something is not implemented in a way that meets these requirements e.g. due to time constraints, explicitly state these shortcomings and explain what would be the correct way of implementing it.

- Code formatting and clarity: “Programs must be written for people to read, and only incidentally for machines to execute.” (Harold Abelson, Structure and Interpretation of Computer Programs)

- Attribution. If you take code from Google results, examples etc., add attributions. We all know new things are often written based on search results.

- Continuous Integration is not evaluated.

## And More
Attached to this email is a file which includes the assignment and the instructions. Please be attentive to the wording and directions of the assignment. Our team will be looking for clean, production-ready code and inclusion of what you consider to be coding “best practices.”

If you have any questions while working on the assignment, please do not hesitate to get in touch with me. I will consult with the team and get back to you with their answers.

Also, I have sent you an invite to a private Github repo to which you can commit your code. Once your assignment is complete, please push the Github link to the comment section within the link below. If you do not complete this step, we cannot grade your home assignment

The engineering team will review your code and provide feedback. If the results are positive, we will then schedule the Team Interview via Google Meet.

We typically offer 7 days to complete this assignment. If anything comes up and you need more time, just let me know.
