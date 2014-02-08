#!/usr/bin/env python
import re

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    page = """
    <h1>{title}</h1>
    <table>
        <tr><th>Author</th><td>{author}</td></tr>
        <tr><th>Publisher</th><td>{publisher}</td></tr>
        <tr><th>ISBN</th><td>{isbn}</td></tr>
    </table>
    <a href="/">Back to the list</a>
    """
    book = DB.title_info(book_id)
    if book is None:
        raise NameError
    return page.format(**book)


def books():
    all_books = DB.titles()
    body = ['<h1>My Bookshelf</h1>', '<ul>']
    item_template = '<li><a href="/book/{id}">{title}</a></li>'
    for book in all_books:
        body.append(item_template.format(**book))
    body.append('</ul>')
    return '\n'.join(body)
    
def resolve_path(path):
    urls = [(r'^$', books),
            (r'^book/(id[\d]+)$', book)]
    matchpath = path.lstrip('/')
    for regexp, func in urls:
        match = re.match(regexp, matchpath)
        if match is None:
            continue
        args = match.groups([])
        return func, args
    # we get here if no url matches
    raise NameError


def application(environ, start_response):
<<<<<<< HEAD
=======
    status = "200 OK"
>>>>>>> upstream/master
    headers = [('Content-type', 'text/html')]
    try:
        path = environ.get('PATH_INFO',None)
        if path is None:
            raise NameError
        func, args = resolve_path(path)
        body = func(*args)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>Internal Server Error</h1>"
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status,headers)
        return [body]
    
    start_response(status, headers)
    return ["<h1>No Progress Yet</h1>", ]
    
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8090, application)
    srv.serve_forever()
