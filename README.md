# Project Overview
Watcher periodically monitors multiple websites, collects performance metrics (timestamp, response time, HTTP status code), and optionally evaluates response content against a configurable regular expression. Metrics are stored in a PostgreSQL database.

URLs, check intervals (5-300 seconds), and regex patterns are configurable individually.

# Design
## Maintainability
> Requirement: Main design goal is maintainability.

Maintainability is broken down into 3 sub-requirements:
1. To lower the **corrective maintainance** cost, which is about reducing bugs and shortening bug-fix turnaround.

    We maintain straightforward code, employe a consistent naming style, ulitize a [linter](./.pylintrc), and incorprate a comprehensive set of [unit test cases](./test/).

2. To lower the **perfective maintenance** cost, especially on further performance tuning.

    We facilitate efficient performance tuning with async operations, connection pools, caching, and configurable parameters

3. To lower the **adaptive maintenance** cost, aiming at adding or removing functionalities.

    We ensure flexibility to adapt to evolving requirements through OOP and clear separation of infrastructure and business logic.

## Scalability and Cost Efficiency
> Requirement: Should work for at least some thousands of separate sites.

The easist way of implementing scalability is to run 1,000 agents on 1,000 VMs, which of course doesn't make business sense. Instead, scalability problem can be treated more as a cost efficiency problem: How to monitor thousands websites with less machines as possible.

- Process as many requests per second as possible on one node, within a pre-defined acceptance level.

- Make the program scalable.
    Keeping the programe stateless, using multiple processed without IPC, partitioning URLs help us to scale out.

- Make the program portable.
    If we can run agents on heterogeneous runtime platforms, whichever is the cheapeast and avaialble. Using docker image helps a lots in term of portability. 


In fact, it is desirable to be able to calculate the unit price per URL so product designer can make informed decisions to gain competition advantage on the market.

## Extensibility and Future-Proofing
> Requirement: Should be production quality

Product quality means that the programme should be resilent to changes in the future.

- There will be new functionality requirements from product onwers.
For example, some URLs might requires Basic Auth, while some other URLs accept POST method only. 

- There will be unpredictable changes of patterns of the input from users. For example, while CPU usually is not the bottleneck for this type of programe, it could be if a user adds 5,000 URLs with a long response which should be evaluated against a complex regular expression like this <code> r"(?=^.*you.*welcome)(?!.*forbidden).*\b(?:[a-zA-Z]{3,6}\s?){2,4}\b(?<=\b[a-zA-Z]+\b)\s\d{1,3}(?<!100|200)\s(?:at|on)\s[0-9]{2}:[0-9]{2}(?=\s(?:AM|PM)$)"</code>

- There network will be very heterogeneous.
For example, some endpoints might reside in an Intranet [10.0.0.0/8](https://en.wikipedia.org/wiki/Private_network), or more challengingly, in DoD/USA's [11.0.0.0/8](https://news.ycombinator.com/item?id=10006534). Then our programe have to be deployed in the same network.
For another example, monitoring a URL that resolves to multiple CDN endpoints from a single node in Finland would provide misleading information to users. Hence, we might be forced to deploy our programe onto many nodes across multiple continents/ISPs/Clouds.

As mentioned above, OOP is used to increase cohesion within a class and reduce coupling between classes, even though it seems to be unneccessary at this moment.

Also, container/shell script are introduced to separate infrastructure code from business logic code so when we redeploy our programe to another runtime platform, the change would be kept within the infrastructure code.


# Implementation
## Structure of code
The program artifact is encapsulated within a [a docker image](./Dockerfile) image, initiated via [an entrypoint script](./entrypoint.sh). This script ensures database readiness and then spawns parallel worker processes based on available CPU cores. [Worker](./src/worker.py) perform concurrent HTTP requests using asyncio and aiohttp, buffering [metrics](./src/metrics.py) that [Keepers](./src/Keeper.py) subsequently commit to the database."

There is also a http server and a endpoints generator for test purpose.

## Concurrency 
> Requirement: we really want to see your take on concurrency.

Three-level concurrency:

- Horizontal scaling across multiple nodes.
- Multi-process parallelism leveraging multiple CPU cores.
- Asynchronous task management within each process using [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/).


Requests to PostgreSQL is done with a sync sdk as I don't have the knowledge to evaluate the maturity of the async libraries, like [asyncpg](https://github.com/MagicStack/asyncpg) and [Psycopg 3](https://www.psycopg.org/psycopg3/docs/advanced/async.html).

## DB Schema
> Requirement: stores the metrics into an PostgreSQL database.

There are 2 tables: a relational table **endpoints** where urls are managed and a timescale hypertable **metrics** which contains the time series data with Timescale plugin.

Please note that **URL** is not used as the primary key since we can have duplicate URLs in case:
- With the same URL, users might specify different regex. 
- If the application is deployed on Intranet, the same url https://10.0.0.1/index" might point to different endpoints.
- When a domain name, for example, https://www.netflix.com/browse, resolves to different CDN IPs, they should be treated as different endpoints.

## Security
As discussed in the previous email, although it is not a good practice to hardcode the DB credentials in a [.env file](./.env), this approach was thought to be acceptable for the purposes of an assignment.

# Future Work
- Add unit test cases for SQL DDL and DML.
- Use an **async** postgresql client to reduce its impact on latency measurement.
- Add an end-2-end test suite
- Build a pipeline to benchmark performance
