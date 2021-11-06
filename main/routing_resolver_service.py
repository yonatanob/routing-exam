from uuid import UUID
from main.routing_service import RoutingService, NoRouteRuleFoundError


class RoutingResolverService:

    def __init__(self, routingService: RoutingService):
        self.routingService = routingService

    def resolve(self, url: str) -> UUID:
        """
        Find a rule by url.
        Exact match is preferred over prefix match, and for prefix match, the longest match wins.
        If no route found, raise NoRouteFound.
        :param url:
        :return: A rule target.
        """
        rule_by_url = self._find_rule_by_url(url=self.routingService.normalize_url(url))
        if rule_by_url:
            return rule_by_url.target
        rule_by_prefix = self._find_rule_by_prefix(url=url)
        if rule_by_prefix:
            return rule_by_prefix.value.target
        else:
            raise NoRouteFoundError(url)

    def _find_rule_by_url(self, url: str):
        """
        Find a rule in the dictionary.
        :param url:
        :return: the rule to be found or None.
        """
        return self.routingService.urls[url] if url in self.routingService.urls else None

    def _find_rule_by_prefix(self, url: str):
        """
        Find a rule in the trie.
        :param url:
        :return: the rule to be found or return (no step) object.
        """
        return self.routingService.url_trie.longest_prefix(url)


class NoRouteFoundError(Exception):
    def __init__(self, url):
        """
        An error if route not found.
        :param url:
        """
        self.message = f'No matching route found for url: {url}'
        super().__init__(self.message)
