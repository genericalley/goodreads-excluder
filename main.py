import click
import re
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from lxml import etree
from requests.api import get


@click.command()
@click.option('--include', default='', help='Comma-delimited genres to '
                                            'include')
@click.option('--exclude', default='', help='Comma-delimited genres to '
                                            'exclude')
@click.option('--api-key', default=None, help='Goodreads developer api key')
@click.option('--threshold', default=15, help='Number of top shelves to check '
                                              'for excluded genres')
def get_new_releases(include, exclude, api_key, threshold):
    include_genres = set(
        normalize_shelf(genre.strip()) for genre in include.split(',')
    )
    exclude_genres = set(
        normalize_shelf(genre.strip()) for genre in exclude.split(',')
    )

    if not include_genres:
        print('You must include at least one genre.')
        raise click.Abort

    if not api_key:
        print(f'You must provide a Goodreads api key'
              f' (https://www.goodreads.com/api/keys).')
        raise click.Abort

    book_ids = set()

    for genre in include_genres:
        book_ids.update(new_books_for_genre(genre))

    for genre in exclude_genres:
        book_ids.difference_update(new_books_for_genre(genre))

    book_xmls = []

    for idx, book in enumerate(book_ids):
        resp = get(
            f'https://www.goodreads.com/book/show/{book}.xml?key={api_key}'
        )
        resp.raise_for_status()
        book_xml = etree.fromstring(resp.content)

        if validate_book(book_xml, exclude_genres, threshold):
            book_xmls.append(book_xml)

        if idx % 5 == 4:
            print(f'Inspected {idx + 1} books.')

        # Goodreads api terms stipulate max 1 request/s
        sleep(1.05)

    final_books = []

    for book in book_xmls:
        title = book.findtext('./book/title')
        author = get_author_string(book)
        url = book.find('./book/link').text
        image_url = book.find('./book/image_url').text

        final_books.append(Book(title, author, url, image_url))

    render_books(final_books, include_genres, exclude_genres)


class Book(object):
    def __init__(self, title, author, url, image_url):
        self.title = title
        self.author = author
        self.url = url
        self.image_url = image_url


def new_books_for_genre(genre):
    resp = get(f'https://www.goodreads.com/genres/new_releases/{genre}')
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    books = soup.find_all('a', href=re.compile('/book/show/'))
    return [book.get('href').split('/')[-1].split('-')[0] for book in books]


def validate_book(book_xml, exclude_genres, threshold):
    popular_shelves = book_xml.findall('./book/popular_shelves/shelf')
    popular_shelf_names = set(
        shelf.values()[0] for shelf in popular_shelves[:threshold]
    )

    for shelf in popular_shelf_names:
        if normalize_shelf(shelf) in exclude_genres:
            print(f'Excluded genre {shelf} detected. '
                  f'Excluding {book_xml.findtext("./book/title")} '
                  f'by {get_author_string(book_xml)}')
            return False

    return True


def normalize_shelf(shelf):
    shelf = shelf.lower()
    shelf = shelf.replace('sci-fi', 'science-fiction')
    shelf = shelf.replace('youngadult', 'young-adult')
    return shelf


def render_books(books, included, excluded):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    filename = f'books-generated-{datetime.now().strftime("%Y%m%d")}.html'
    template.stream(
        books=sorted(books, key=lambda book: book.author),
        included=', '.join(sorted(included)),
        excluded=', '.join(sorted(excluded)),
    ).dump(filename)
    print(f'Done. See your new releases in {filename}')


def get_author_string(book_xml):
    return ', '.join([
        author.text for author
        in book_xml.findall('./book/authors/author/name')
    ])


if __name__ == '__main__':
    get_new_releases()
