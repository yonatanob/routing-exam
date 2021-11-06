from flask import Flask, request, redirect
from uuid import uuid4

from main.routing_service import RoutingService, NoRouteRuleFoundError
from main.routing_resolver_service import RoutingResolverService, NoRouteFoundError
from main.routing_rules import CreateRouteRule, RouteRule

app = Flask(__name__)
targets = {}  # uuid : target, Holds all uuid of the input targets
routing_service = RoutingService()
routing_resolver = RoutingResolverService(routing_service)


@app.route('/create', methods=['POST'])
def create_post():
    """
    Stores the user input in the DS using routing_service.create()
    :return: redirect('/create') - reload the same page
    """
    exact_match_from_user = True if "exact_match" in request.form and \
                                    request.form["exact_match"] == "on" else False
    uuid = uuid4()
    targets[uuid] = request.form["target"]

    new_create = CreateRouteRule(url=request.form["url"], target=uuid, exact_match=exact_match_from_user)
    try:
        routing_service.create(createRequest=new_create)
        routing_service.validate_url(url=request.form["target"])  # make sure 'target' is not empty
    except:
        return redirect('/notValidInput')

    return redirect('/create')


@app.route('/create')
def create_page():
    """
    Create a form for user to the '/create' page.
    :return: The form
    """
    return "<form method='post' >" \
           "<input type='url' name='url' placeholder='url'/>" \
           "<input type='url' name='target' placeholder='target' />" \
           "<input type='checkbox' name='exact_match' placeholder='exact_match' />" \
           "<input type='submit'>" \
           "<br><a href='/'>Go to resolve page</a>" \
           "</form>"


@app.route('/redirect', methods=['GET'])
def get_post():
    """
    Find the target using routing_resolver.resolve() and redirect to it, else redirect to '/noMatch' page.
    :return: Redirect to (target or '/noMatch')
    """
    try:
        # gets the user url input and find its uuid
        uuid = routing_resolver.resolve(request.args.get("url"))
    except:
        return redirect('/noMatch')

    return redirect(targets[uuid])


@app.route('/')
def get_page():
    """
    Create a form for user to the '/' page.
    :return: The form
    """
    return "<form method='get' action='/redirect'>" \
           "<input type='url' name='url' placeholder='url to find' />" \
           "<input type='submit'>" \
           "<br><a href='/create'>Go to create page</a>" \
           "</form> "


@app.route('/noMatch')
def noMatch():
    """
    Create a page for user to the '/noMatch' page.
    :return: The page
    """
    return "<!DOCTYPE html>" \
           "<html>" \
           "<body>" \
           "<h1>No match!</h1>" \
           "<br><a href='/'>Go back</a>" \
           "</body>" \
           "</html>"


@app.route('/notValidInput')
def notValidInput():
    """
    Create a page for user to the '/notValidInput' page.
    :return: The page
    """
    return "<!DOCTYPE html>" \
           "<html>" \
           "<body>" \
           "<h1>Not a valid url input</h1>" \
           "<br><a href='/create'>Go back</a>" \
           "</body>" \
           "</html>"


if __name__ == '__main__':
    app.run()
