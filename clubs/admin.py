from django.contrib import admin
from .models import User, Post, Club, Book

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'username', 'first_name', 'last_name', 'email', 'is_active',
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for posts."""

    list_display = [
        'get_author', 'text', 'created_at',
    ]

    def get_author(self, post):
        """Return the author of a given post."""
        return post.author.username

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'name', 'owner_name', 'location', 'description', 'member_list',
    ]

    def owner_name(self, Club):
        return Club.owner.first_name + ' ' + Club.owner.last_name

    def member_list(self, Club):
        return "\n".join([member.first_name for member in Club.members.all()])
        

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for books."""

    list_display = [
        'ISBN', 'title', 'author', 'publication_year'
    ]
