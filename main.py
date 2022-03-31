from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegisterForm, LoginForm, BooksForm, AuthorForm, \
    InputForm, GenreForm, AuthorSearch, GenreSearch, PriceSearch, BookReview
import wikipediaapi
from data.users import User
from data.books import Books
from data.author import Author
from data.genres import Genre

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
wiki_wiki = wikipediaapi.Wikipedia('ru')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/main', methods=['GET', 'POST'])
def index():
    form = InputForm()
    if form.validate_on_submit():
        message = form.message.data
        answer = request.form['req']
        return sent(message, answer)
    return render_template("main.html", title='Главная', form=form, warning='')


@login_required
def sent(message, answer):
    answers = ['Книга(введите название)', 'Автор(введите имя и фамилию)']
    a = answers.index(answer)
    form = InputForm()
    if a == 0:
        session = db_session.create_session()
        book = session.query(Books).filter(Books.title == message).first()
        if book:
            author = session.query(Author).filter(Author.id == book.author_id).first()
            genre = session.query(Genre).filter(Genre.id == book.genre_id).first().genre
            b = "_".join(book.title.strip().split())
            url = f'https://ru.wikipedia.org/wiki/{b}'
            return render_template('books.html', title='Книга', books=[book], names=[author.name],
                                   surnames=[author.surname], extra_info=[url], genres=[genre], err='')
        return render_template('books.html', title='Книга', err='Данной книги у нас нет в наличии')
    elif a == 1:
        session = db_session.create_session()
        name, surname = message.split()
        author = session.query(Author).filter(Author.name == name, Author.surname == surname).first()
        if author:
            url = f'https://ru.wikipedia.org/wiki/{author.name} {author.surname}'
            return render_template('authors.html', title='Автор', authors=[author], extra_info=[url], err='')
        return render_template('authors.html', title='Автор', err='Книг данного писателя у нас нет в наличии')


@app.route('/searchauthor', methods=['GET', 'POST'])
@login_required
def search_by_author():
    form = AuthorSearch()
    if form.validate_on_submit():
        surname = form.surname.data
        session = db_session.create_session()
        author = session.query(Author).filter(Author.surname == surname).first()
        if not author:
            return render_template('search_author.html', title='Фильтрация по автору', form=form, message='Книг такого автора у нас нет')
        books = session.query(Books).filter(Books.author_id == author.id).all()
        genres, url = [], []
        for book in books:
            genres.append(session.query(Genre).filter(Genre.id == book.genre_id).first().genre)
            b = "_".join(book.title.strip().split())
            url_ = f'https://ru.wikipedia.org/wiki/{b}'
            url.append(url_)
        return render_template('books.html', title='Фильтрация по автору', books=books,
                               surnames=[author.surname] * len(books), names=[author.name] * len(books),
                               genres=genres, extra_info=url, message='')
    return render_template("search_author.html", title='Фильтрация по автору', form=form, message='')


@app.route('/searchgenre', methods=['GET', 'POST'])
@login_required
def search_by_genre():
    form = GenreSearch()
    if form.validate_on_submit():
        genre = form.genre.data.lower()
        session = db_session.create_session()
        genre = session.query(Genre).filter(Genre.genre == genre).first()
        if not genre:
            return render_template('search_genre.html', title='Фильтрация по жанру', form=form,
                                   message='Книг такого жанра у нас нет')
        books = session.query(Books).filter(Books.genre_id == genre.id).all()
        names, surnames, url = [], [], []
        for book in books:
            author = session.query(Author).filter(Author.id == book.author_id).first()
            names.append(author.name)
            surnames.append(author.surname)
            b = "_".join(book.title.strip().split())
            url_ = f'https://ru.wikipedia.org/wiki/{b}'
            url.append(url_)
        return render_template('books.html', title='Фильтрация по жанру', books=books,
                               surnames=surnames, names=names,
                               genres=[genre.genre] * len(books), extra_info=url, message='')
    return render_template("search_genre.html", title='Фильтрация по жанру', form=form, message='')


@app.route('/searchprice', methods=['GET', 'POST'])
@login_required
def search_by_price():
    form = PriceSearch()
    if form.validate_on_submit():
        minimum = form.minimum.data
        maximum = form.maximum.data
        if minimum > maximum:
            return render_template('search_price.html', title='Фильтрация по цене', form=form,
                                   message='Перепутаны минимальное и максимальное значения')
        session = db_session.create_session()
        books = session.query(Books).filter(Books.price >= minimum, Books.price <= maximum).all()
        if not books:
            return render_template('search_price.html', title='Фильтрация по цене', form=form,
                                   message='В магазине нет книг в такой ценовой категории.')
        names, surnames, url, genres = [], [], [], []
        for book in books:
            author = session.query(Author).filter(Author.id == book.author_id).first()
            genres.append(session.query(Genre).filter(Genre.id == book.genre_id).first().genre)
            names.append(author.name)
            surnames.append(author.surname)
            b = "_".join(book.title.strip().split())
            url_ = f'https://ru.wikipedia.org/wiki/{b}'
            url.append(url_)
        return render_template('books.html', title='Фильтрация по жанру', books=books,
                               surnames=surnames, names=names,
                               genres=genres, extra_info=url, message='')
    return render_template("search_price.html", title='Фильтрация по жанру', form=form, message='')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    user.bought = ''
    session.commit()
    logout_user()
    return redirect("/")


@app.route('/authors')
def authors():
    session = db_session.create_session()
    authors = session.query(Author).all()
    extra_info = []
    for author in authors:
        page_py = wiki_wiki.page(f'{author.name}_{author.surname}')
        extra_info.append(page_py.fullurl)
        a = page_py.text.split()
    return render_template('authors.html', title='Все авторы', authors=authors, extra_info=extra_info)


@app.route('/genres')
def genres():
    session = db_session.create_session()
    genres = session.query(Genre).all()
    extra_info = []
    for genre in genres:
        page_py = wiki_wiki.page(f'{genre.genre}')
        extra_info.append(page_py.fullurl)
    return render_template('genres.html', title='Все жанры', genres=genres, extra_info=extra_info)


@app.route('/genres/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_authors(id):
    form = GenreForm()
    if request.method == "GET":
        session = db_session.create_session()
        genre = session.query(Genre).filter(Genre.id == id,
                                          current_user.id == 1).first()
        if genre:
            form.genre.data = genre.genre
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        genre = session.query(Genre).filter(Genre.id == id,
                                            current_user.id == 1).first()
        if genre:
            genre.genre = form.genre.data
            session.commit()
            return redirect('/genres')
        else:
            abort(404)
    return render_template('addgenre.html', title='Редактирование жанров', form=form)


@app.route('/books')  # не работает
def books():
    session = db_session.create_session()
    books = session.query(Books).all()
    names, surnames, genres, extra_info = [], [], [], []
    for book in session.query(Books).all():
        author = session.query(Author).filter(Author.id == book.author_id).first()
        genre = session.query(Genre).filter(Genre.id == book.genre_id).first()
        genres.append(genre.genre)
        names.append(author.name)
        surnames.append(author.surname)
        b = "_".join(book.title.strip().split())

        page_py = wiki_wiki.page(f'{b}')
        extra_info.append(page_py.fullurl)

    return render_template('books.html', title='Все книги', books=books, names=names, surnames=surnames,
                           extra_info=extra_info, genres=genres)


def main():
    db_session.global_init("db/book_shop.sqlite")
    app.run()


if __name__ == '__main__':
    main()

