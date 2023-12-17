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
