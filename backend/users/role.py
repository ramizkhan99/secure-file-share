class UserRole:
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'

    CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
        (GUEST, 'Guest')
    ]