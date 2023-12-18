# Cover letter
I am very fond of Aiven's product and its value proposition, to which I believe I can significantly contribute if given the opportunity to join the team. This is why I completed the assignment, even though I was informed by Irina that the role had been cancelled.

# Design: the Desired, the Avoided and the Tradeoff

## Tradeoff between Maintainability and Extensibility/Performance
> Requirement: Main design goal is maintainability.

Maintainability is broken down into 3 sub-requirements:
1. To lower the corrective maintainance cost, which is about reduceing number of bugs and reducing the time to fix bugs.

    Maintaining straightforward code, employing a consistent naming style, utilizing a [linter](./.pylintrc), and incorporating a comprehensive set of [unit test cases](./test/) are essential steps.

2. To lower the perfective maintenance cost, especially on further performance tuning.

    Async functions, connection pools, configurable parameters and caches are introduced to make performance tuning possible when needed.

3. To lower the adaptive maintenance cost, aiming at adding or removing functionalities to adapt to a dynamic business environment.

    OOP, decoupling of infrastructure and business logics are used. Details will be disussed later.

Obviously, #2/#3 have some interest conflicts with #1 since they introduce code that are not so straightforward. To mitigate this conflict, beside trying my best to strike a balance, I also write lots of documentations and comments, which might be a bit too excessive.

## How is Performance Defined?
> Requirement: Should work for at least some thousands of separate sites.

This goal can be achieved by running terrible code on a thousand VMs, which of course doesn't make business sense. So I would interprete this requirement in this way:
- Make the programme scalable.

    So when needed, we can scale out the program onto multiple nodes, instead of to tune its performance on a single node.
    Keeping the programe stateless, using multiple processed without IPC, partitioning URLs help with scalability.
- Make the program portable.

    So we can run it on heterogeneous runtime platforms, whichever is the cheapeast and avaialble. Using docker image helps a lots in term of portability. 
- Process as many RPS(requests per second) as possible on one node, within a pre-defined acceptance level.

    So our offering would gain competition advantage on the market. In fact, it is desirable to be able to calculate the unit price per URL in real time so product owner can make informed decisions.

## Extensibility: Seperate the parts that change from the parts that doesn't change
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

## Conflict between Performance and Accurancy 
Although attaining the highest RPS is desirable, it's crucial to ensure the program doesn't significantly contribute to latency or cause request failures Otherwise, instead of monitoring the latency/availability of the target URLs, we would end up monitoring the performance of our own agents.

Observability and A/B test can be used to help strike a balance between performance and accurancy. For example, if a localhost URL's latency reaches 5 seconds, it is most likely that the latency comes from the agents, instead of from the targets.

Observabilty and A/B test is an ongoing operation, instead of a single design decision.

However, it is assumed be to acceptable to lose a small amount of time-series data to reduce complexity and infrastructure cost.


# Implementation
## Structure of code
The programe artifact is [a docker image](./Dockerfile), with [a entrypoint script](./entrypoint.sh) that sequentially performs two primary functions:
1. Assure database is ready.
2. Start multiple processes in parrelel, number of which is decided by the number of CPU cores available.

Then in every process, there is one [Worker](./src/worker.py), which use coroutines to sends HTTP requests to each [Endpoint](./src/endpoint.py) and put the [metrics](./src/metrics.py) of latency, status code, regex evaluation result into a buffer. Also, some number of [Keepers](./src/Keeper.py) are provisioned to dump the stats into DB. 

There is also a http server and a endpoints generator for test purpose.

## Concurrency 
> Requirement: we really want to see your take on concurrency.

Concurrency within the program is achieved at three levels:

1. Deploying the programme onto multiple nodes to utilize a cluster.
2. Start multiple processed on one node to utilize multiple cores.
3. Within one process, all requests and keeper coroutines are scheduled by one event loop so there is no multiple threads.
4. Within one process, [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) have been chosen for concurrency.
5. Requests to PostgreSQL is done with a sync sdk as I don't have the knowledge to evaluate the maturity of the async libraries, like [asyncpg](https://github.com/MagicStack/asyncpg) and [Psycopg 3](https://www.psycopg.org/psycopg3/docs/advanced/async.html).

## DB Schema
> Requirement: stores the metrics into an Aiven PostgreSQL database.

There are 2 tables: a relational table **endpoints** where urls are managed and a timescale hypertable **metrics** which contains the time series data with Timescale plugin.

Please note that **URL** is not used as the primary key since we can have duplicate URLs in case:
- With the same URL, users might specify different regex. 
- If the application is deployed on Intranet, the same url https://10.0.0.1/index" might point to different endpoints.
- When a domain name, for example, https://www.netflix.com/browse, resolves to different CDN IPs, they should be treated as different endpoints.
- If Aiven provides url-monitoring-as-a-service and 2 users might specify the same URL and Aiven should be able to distinguish them.

## Security
As discussed in the previous email, although it is not a good practice to hardcode the DB credentials in a [.env file](./.env), this approach was thought to be acceptable for the purposes of an assignment.

# Todos
- Add unit test cases for SQL DDL and DML.
- Use an **async** postgresql client to reduce its impact on latency measurement.
- Choose a more performant data structure than asyncio.Queue()
- Add an end-2-end test suite
- Use Datadog to build observability
- Build a pipeline to benchmark performance
