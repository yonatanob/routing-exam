import unittest
import uuid
import random
import string
from main.routing_service import RoutingService, NoRouteRuleFoundError
from main.routing_resolver_service import RoutingResolverService, NoRouteFoundError
from main.routing_rules import CreateRouteRule, RouteRule
from pydantic import BaseModel, HttpUrl, ValidationError


class RoutingTest(unittest.TestCase):
    _domain_size = 10

    def setUp(self):
        self._routing_service = RoutingService()
        self._routing_resolver_service = RoutingResolverService(self._routing_service)

    # passed
    def test_create_route_rule(self):
        target = uuid.uuid4()
        url = self._random_url()
        route_rule_id = self._routing_service.create(CreateRouteRule(url=url, target=target, exact_match=True))

        expected = RouteRule(url=url, target=target, exact_match=True, routing_rule_id=route_rule_id)
        response = self._routing_service.get(route_rule_id)
        self.assertEqual(response, expected)

    # passed
    def test_resolve_non_existing_single_rule_exact_match(self):
        target = uuid.uuid4()
        existing_url = self._random_url()
        non_existing_url = self._random_url()

        self._routing_service.create(CreateRouteRule(url=existing_url, target=target, exact_match=True))
        self.assertRaises(NoRouteFoundError, self._routing_resolver_service.resolve, non_existing_url)

    # passed
    def test_resolve_non_existing_single_rule_prefix_match(self):
        target = uuid.uuid4()
        base_url = self._random_url()
        existing_url = f'{base_url}/abc'
        non_existing_url = f'{base_url}/abcd'

        self._routing_service.create(CreateRouteRule(url=existing_url, target=target, exact_match=False))

        # resolving {base_url}/abc/d instead, would expect a match.
        self.assertRaises(NoRouteFoundError, self._routing_resolver_service.resolve, non_existing_url)

    # passed - my test - checking the above comment
    def test_resolve_non_existing_single_rule_prefix_match_my_test_checking_comment(self):
        target = uuid.uuid4()
        base_url = self._random_url()
        existing_url = f'{base_url}/abc'
        non_existing_url = f'{base_url}/abc/d'

        self._routing_service.create(CreateRouteRule(url=existing_url, target=target, exact_match=False))

        non = self._routing_resolver_service.resolve(non_existing_url)
        exist = self._routing_resolver_service.resolve(existing_url)
        self.assertEqual(exist, non)

    # passed
    def test_resolve_match_path_exact_match(self):
        target1 = uuid.uuid4()
        base_url = self._random_url()
        self._routing_service.create(CreateRouteRule(url=base_url, target=target1, exact_match=True))

        target2 = uuid.uuid4()
        url2 = f'{base_url}/a'
        self._routing_service.create(CreateRouteRule(url=url2, target=target2, exact_match=True))

        target3 = uuid.uuid4()
        url3 = f'{base_url}/a/b'
        self._routing_service.create(CreateRouteRule(url=url3, target=target3, exact_match=True))

        response = self._routing_resolver_service.resolve(url2)
        self.assertEqual(response, target2)

    # passed
    def test_resolve_match_path_prefix_match(self):
        target1 = uuid.uuid4()
        base_url = self._random_url()
        self._routing_service.create(CreateRouteRule(url=base_url, target=target1, exact_match=True))

        target2 = uuid.uuid4()
        url2 = f'{base_url}/a'
        self._routing_service.create(CreateRouteRule(url=url2, target=target2, exact_match=False))

        target3 = uuid.uuid4()
        url3 = f'{base_url}/a/b'
        self._routing_service.create(CreateRouteRule(url=url3, target=target3, exact_match=False))

        target4 = uuid.uuid4()
        url4 = f'{base_url}/a/b/c'
        self._routing_service.create(CreateRouteRule(url=url4, target=target4, exact_match=False))

        response = self._routing_resolver_service.resolve(url=f'{base_url}/a/b/d')
        self.assertEqual(response, target3)

    # passed
    def test_resolve_match_path_prefer_exact_match_over_prefix_match(self):
        base_url = self._random_url()

        target1 = uuid.uuid4()
        url1 = f'{base_url}/a/b'
        self._routing_service.create(CreateRouteRule(url=url1, target=target1, exact_match=True))

        target2 = uuid.uuid4()
        url2 = f'{base_url}/a'
        self._routing_service.create(CreateRouteRule(url=url2, target=target2, exact_match=False))

        response = self._routing_resolver_service.resolve(f'{base_url}/a/b')
        self.assertEqual(response, target1)

    # passed
    def test_resolve_match_path_query_params_included_match(self):
        target = uuid.uuid4()
        base_url = self._random_url()
        url = f'{base_url}?key=value'

        self._routing_service.create(CreateRouteRule(url=url, target=target, exact_match=True))
        response = self._routing_resolver_service.resolve(url)

        self.assertEqual(response, target)

    # passed
    def test_resolve_match_path_query_params_included_no_match(self):
        target = uuid.uuid4()
        base_url = self._random_url()
        existing_url = f'{base_url}?key1=value1&key2=value2'
        non_existing_url = f'{base_url}?key1=value1'

        self._routing_service.create(CreateRouteRule(url=existing_url, target=target, exact_match=True))

        self.assertRaises(NoRouteFoundError, self._routing_resolver_service.resolve, non_existing_url)

    # passed
    def test_resolve_match_path_query_params_included_out_of_order(self):
        target = uuid.uuid4()
        base_url = self._random_url()
        url = f'{base_url}?key1=value1&key2=value2'
        out_of_order_url = f'{base_url}?key2=value2&key1=value1'

        self._routing_service.create(CreateRouteRule(url=url, target=target, exact_match=True))
        response = self._routing_resolver_service.resolve(out_of_order_url)

        self.assertEqual(response, target)

    # passed
    def test_resolve_match_path_50k_rules_different_domains(self):
        prefix = "domain"
        rules = [CreateRouteRule(url=self._random_url(prefix), target=uuid.uuid4(), exact_match=True) for i in
                 range(50000)]
        for rule in rules:
            self._routing_service.create(rule)

        chosen_rule = random.choice(rules)
        response = self._routing_resolver_service.resolve(chosen_rule.url)

        self.assertEqual(response, chosen_rule.target)

    # passed
    def test_resolve_match_path_50k_rules(self):
        base_url = self._random_url()
        rules = [CreateRouteRule(url=f'{base_url}/{self._random_url_friendly_string()}', target=uuid.uuid4(),
                                 exact_match=True) for i in range(50000)]
        for rule in rules:
            self._routing_service.create(rule)

        chosen_rule = random.choice(rules)
        response = self._routing_resolver_service.resolve(chosen_rule.url)

        self.assertEqual(response, chosen_rule.target)

    def _random_url_friendly_string(self):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(self._domain_size))

    def _random_url(self, prefix=""):
        domain = self._random_url_friendly_string()
        return f"https://www.{prefix}{domain}.com"

# my tests:

    # checking for a non-existing route rule UUID
    def test_Routing_Service_get_non_existing(self):
        target = uuid.uuid4()
        url = self._random_url()
        self._routing_service.create(CreateRouteRule(url=url, target=target, exact_match=True))

        self.assertRaises(NoRouteRuleFoundError, self._routing_service.get, target)

    def test_empty_string_input(self):
        target = uuid.uuid4()
        url = ""
        rule_obj = CreateRouteRule(url=url, target=target, exact_match=True)
        self.assertRaises(ValidationError, self._routing_service.create, rule_obj)

    def test_not_valid_url(self):
        target = uuid.uuid4()
        url = "google.com"  # no scheme
        rule_obj = CreateRouteRule(url=url, target=target, exact_match=True)
        self.assertRaises(ValidationError, self._routing_service.create, rule_obj)

    def test_not_valid_query_prefix(self):
        target = uuid.uuid4()
        url = "google.com/123/12/?"  # not valid, starts with '?' without query
        rule_obj = CreateRouteRule(url=url, target=target, exact_match=True)
        self.assertRaises(ValidationError, self._routing_service.create, rule_obj)

    def test_not_valid_query_vars(self):
        target = uuid.uuid4()
        url = "google.com/123/12/?a="  # not valid, without query vars
        rule_obj = CreateRouteRule(url=url, target=target, exact_match=True)
        self.assertRaises(ValidationError, self._routing_service.create, rule_obj)

    def test_create_duplicate_url(self):
        target1 = uuid.uuid4()
        url1 = self._random_url()

        rule_obj1 = CreateRouteRule(url=url1, target=target1, exact_match=True)
        self._routing_service.create(rule_obj1)
        self._routing_resolver_service.resolve(rule_obj1.url)

        target2 = uuid.uuid4()
        url2 = url1
        rule_obj2 = CreateRouteRule(url=url2, target=target2, exact_match=True)
        self._routing_service.create(rule_obj2)

        response2 = self._routing_resolver_service.resolve(rule_obj2.url)
        response3 = self._routing_resolver_service.resolve(rule_obj1.url)

        self.assertEqual(response2, response3)


if __name__ == '__main__':
    unittest.main()
