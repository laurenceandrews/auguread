from django.contrib import admin

from .models import (Address, Book, Book_Rating, Club, Club_Book_History,
                     Club_Books, Club_Users, ClubFeedPost, MeetingAddress,
                     MeetingLink, Post, User, User_Book_History, User_Books)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id',
        'username',
        'clubs_attended',
        'friends_list'
    ]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs."""

    list_display = [
        'name', 'location', 'calendar', 'meeting_type', 'applicants_count', 'members_count', 'owners_count', 'favourite_books'
    ]

    def applicants_count(self, club):
        """Return the number of club applicants."""
        return club.applicants().count()

    def members_count(self, club):
        """Return the number of club applicants."""
        return club.members().count()

    def owners_count(self, club):
        """Return the number of club members."""
        return club.owners().count()


@admin.register(Club_Users)
class Club_UsersAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club users."""

    list_display = [
        'club_name', 'user', 'role_num'
    ]

    def club_name(self, club):
        """Return the name of the club of the club_user."""
        return club.club.name


@admin.register(Book_Rating)
class BookRatingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for book ratings."""

    list_display = [
        'user', 'book_title', 'rating'
    ]

    def book_title(self, book_rating):
        """Return the title of an book rating's book."""
        return book_rating.book.title


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for posts."""

    list_display = [
        'get_author', 'text', 'created_at',
    ]

    def get_author(self, post):
        """Return the author of a given post."""
        return post.author.username


@admin.register(ClubFeedPost)
class ClubFeedPostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club feed posts."""

    list_display = [
        'club_name', 'post_text'
    ]

    def club_name(self, club_feed_post):
        """Return the name of the club."""
        return club_feed_post.club.name

    def post_text(self, club_feed_post):
        """Return the author of a given post."""
        return club_feed_post.post.text


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for books."""

    list_display = [
        'ISBN', 'title', 'author', 'publication_year'
    ]


@admin.register(User_Book_History)
class User_Book_History(admin.ModelAdmin):
    """Configuration of the admin interface for user book history."""

    list_display = [
        'user', 'book'
    ]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for addresses."""

    list_display = [
        'name', 'zip_code', 'city', 'country'
    ]


@admin.register(MeetingAddress)
class MeetingAddressAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for meeting addresses."""

    list_display = [
        'event', "address_name"
    ]

    def address_name(self, meeting_address):
        """Return the name of an address."""
        return meeting_address.address.name


@admin.register(MeetingLink)
class MeetingLinkAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for meeting links."""

    list_display = [
        'event', 'meeting_link'
    ]


@admin.register(Club_Books)
class Club_BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club users."""

    list_display = [
        'club', 'book'
    ]


@admin.register(Club_Book_History)
class Club_Book_HistoryAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club book history."""

    list_display = [
        'club', 'book'
    ]


@admin.register(User_Books)
class User_BooksAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for User_Books (user's favourite books)."""

    list_display = [
        'user', 'book'
    ]
