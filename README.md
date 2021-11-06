# Route Resolving

## Note:
To view the readme in http style view (like in github) use https://markdownlivepreview.com/

## Description:
At Wix, when receiving a request to render a site, we first need to lookup the site by the provided URL.
For this assignment, a URL has the format of `<domain>/<path>?<query params>`, where `query params` are a list of `key=val` separated with an `&` char.

Each such URL can have multiple Routing Rules defined.
You can assume there are no more than 50k rules per domain. 

For example:
* www.domain.com → rendering site 1.
* www.domain.com/a → rendering site 2.
* www.domain.com/a?param=val → rendering site 3.

Routing rule can be either an `Exact Match` rule, or a `Prefix Match` rule. For the latter, a simple longest prefix match is assumed.

You can assume that no one creates a Prefix Match routing rule with query params.

Rules are defined as follows:

| Type  | Description  | Example |
| ----------- | ----------- | ----------- |
|Exact Match|URL should match exactly the one defined|Routing rule: (www.domain.com/one, exactMatch = true) => X<br><br> Input: www.domain.com/one => Output: <b>match X!<b> <br>Input: www.domain.com/one/two => Output: <b>no match!<b>|
|Prefix Match|URL can match rules with some given prefix|Routing rules: <br>-(www.domain.com/one, exactMatch = false) => X <br>-(www.domain.com/one/two, exactMatch = true) => Y <br><br>Input: www.domain.com/one/two/some-page => Output: <b>match X!<b><br>Input: www.domain.com/one/some-page => Output: <b>match X!<b><br>Input: www.domain.com/one/two => Output: <b>match Y!<b><br>Input: www.domain.com/some-page => Output: <b>no match!<b><br>Input: www.domain.com/oneeee => Output: <b>no match!<b>|


Your task is to implement:
1. Routing Rules management API (CRUD), to manage the routing rules.
2. Resolve API: find the **best site matching a given domain + path + query params which can be out of order. 

**Exact match is preferred over prefix match, and for prefix match, the longest match wins. 
If no route found, throw NoRouteFound. 
    
_Tips_:
- Start simple by making tests pass one by one.
- No need for persistency level.
- Feel free to add more tests if needed. 
- Pay attention to efficiency. 
- Pay attention to the modularity of your code. 
- Feel free to use Google

## Dependencies
- Python 3.7 and up
- pip install pydantic

## How do I start?
routing_service.py & routing_resolver_service.py are the entry points of the Route Resolver server. 
Start with running test_routing.py and implement the missing logic.
From shell:
`python3 -m unittest discover -v test`

## Troubleshooting
If you get trouble to maven test the project, please try to reload all maven project, via maven plugin on your IDE. 