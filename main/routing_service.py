from uuid import UUID, uuid4
from pydantic import BaseModel, HttpUrl, ValidationError  # pip install pydantic
from main.routing_rules import RouteRule, CreateRouteRule
from pygtrie import StringTrie  # pip install pygtrie


class RoutingService:
    """
        # explain later
    """

    def __init__(self):
        self.url_trie = StringTrie(separator="/")  # for radix tree
        self.route_rules = dict()  # hash table
        self.urls = dict()

    def get(self, routing_rule_id: UUID) -> RouteRule:
        """
        Gets the Route rule object by id ir raise an error.
        :param routing_rule_id: routing rule UUID
        :return: A route rule.
        """
        if routing_rule_id in self.route_rules:
            return self.route_rules[routing_rule_id]
        raise NoRouteRuleFoundError(routing_rule_id)

    def create(self, createRequest: CreateRouteRule) -> UUID:
        """
        Create a new route rule and insert the new rule to the correct DS.

        :param createRequest: CreateRouteRule
        :return: new_UUID: The route rule id.
        """
        new_UUID = uuid4()  # generate a new routing rule id

        self.validate_url(url=createRequest.url)
        self.route_rules[new_UUID] = RouteRule(
                                            url=createRequest.url,
                                            target=createRequest.target,
                                            exact_match=createRequest.exact_match,
                                            routing_rule_id=new_UUID)

        current_rule = RouteRule(
                                routing_rule_id=new_UUID,
                                target=createRequest.target,
                                url=self.normalize_url(createRequest.url),
                                exact_match=createRequest.exact_match)

        self.urls[self.normalize_url(createRequest.url)] = current_rule

        if not createRequest.exact_match:  # if exact_match is True, no need to include in the trie
            self.url_trie[createRequest.url] = current_rule
        return new_UUID

    def parse_url_params(self, url: str):
        """
        Parse the URL to two formatted variables
        :param url: str
        :return:
                parsed_url - (baseUrl,sorted_query_params or None)
                baseUrl : str : <scheme>://<domain>/<path>
                sorted_query_params : sorted list of unique query parameters : list[key=val,...]
        """
        url_obj = URLModel(url=url)
        baseUrl = url_obj.url.scheme + "://" + url_obj.url.host
        if url_obj.url.path:
            baseUrl += url_obj.url.path
        else:
            baseUrl += '/'
        sorted_query_params = None
        if url_obj.url.query:  # sorts only if there are query params
            sorted_query_params = sorted(set(url_obj.url.query.split('&')))
        parsed_url = (baseUrl, sorted_query_params)
        return parsed_url

    def normalize_url(self, url: str):
        """
        Normalize a URL to the given format:
        <scheme>://<domain>/<path>?<query params>
        where `query params` are a list of `key=val` separated with an `&` char.
        <path>,<query params> are optional

        :param url: str
        :return: A normalized URL
        """
        baseUrl, query_params = self.parse_url_params(url=url)
        url = baseUrl
        if query_params:
            url += "?" + '&'.join(query_params)
        return url

    def validate_url(self, url: str):
        """
        Checks validity of a URL.
        :param url: str
        :return: A URLModel object or raise a validation error
        """
        return URLModel(url=url)


class NoRouteRuleFoundError(Exception):
    def __init__(self, routing_rule_id):
        """
        An error if route rule not found
        :param routing_rule_id:
        """
        self.message = f'No route rule found for {routing_rule_id}'
        super().__init__(self.message)


class URLModel(BaseModel):
    """
    An object of pydantic.HttpUrl
    """
    url: HttpUrl
