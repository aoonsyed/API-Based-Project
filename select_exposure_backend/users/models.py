from django.utils import timezone

from django.db import models

ROLES = (
    ('user', 'User'),
    ('contributor', 'Content Contributor'),
    ('admin', 'Admin'),
)

GENDERS = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

SKIN_TONES = (
    ('light', 'Light'),
    ('medium', 'Medium'),
    ('dark', 'Dark'),
)

HAIR_COLORS = (
    ('blonde', 'Blonde'),
    ('brown', 'Brown'),
    ('black', 'Black'),
    ('red', 'Red'),
    ('auburn', 'Auburn'),
    ('dirty_blonde', 'Dirty Blonde'),
    ('strawberry_blonde', 'Strawberry Blonde'),
    ('other', 'Other'),
)

BODY_TYPES_MALE = (
    ('short_thin', 'Short & Thin'),
    ('short_broad', 'Short & Broad'),
    ('athletic', 'Athletic/Average'),
    ('tall_slim', 'Tall & Slim'),
    ('big_tall', 'Big & Tall'),
)

BODY_TYPES_FEMALE = (
    ('petite', 'Petite'),
    ('tall_slender', 'Tall & Slender'),
    ('athletic', 'Athletic/Average'),
    ('curvy', 'Curvy'),
    ('plus_size', 'Plus Size'),
)


class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    screen_name = models.CharField(max_length=150)
    role = models.CharField(choices=ROLES, max_length=20, default='user')
    card_details = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.role}"


class ContributorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contributor_profile')
    legal_full_name = models.CharField(max_length=255)
    show_name_public = models.BooleanField(default=False)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(choices=GENDERS, max_length=10)
    height = models.CharField(max_length=20)
    weight = models.CharField(max_length=20)
    shoe_size = models.CharField(max_length=10)
    skin_tone = models.CharField(choices=SKIN_TONES, max_length=10)
    hair_color = models.CharField(choices=HAIR_COLORS, max_length=20)
    body_type_male = models.CharField(choices=BODY_TYPES_MALE, max_length=20, blank=True, null=True)
    body_type_female = models.CharField(choices=BODY_TYPES_FEMALE, max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} ContributorProfile"

    @property
    def age(self):
        from datetime import date
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Invite(models.Model):
    INVITE_METHODS = (
        ('email', 'Email'),
        ('sms', 'SMS'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('joined', 'Joined'),
        ('failed', 'Failed'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=INVITE_METHODS)
    recipient = models.CharField(max_length=255)  # email or phone number
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email} invited {self.recipient} via {self.method}"


class Contest(models.Model):
    CATEGORY_CHOICES = (
        ('Hand', 'Hand'),
        ('Face', 'Face'),
        ('Legs', 'Legs'),
        ('Feet', 'Feet'),
        ('Teaser', 'Teaser'),
        ('Full Body', 'Full Body'),
    )

    name = models.CharField(max_length=255)
    gallery = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Full Body')
    image_url = models.URLField(blank=True, null=True)
    estimated_prize = models.CharField(max_length=50, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.name} ({self.category})"

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()


class ContestEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contest')

    def __str__(self):
        return f"{self.user.email} joined {self.contest.name}"


class ContestPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    upvotes = models.PositiveIntegerField()
    win_date = models.DateField()

    def __str__(self):
        return f"{self.user.screen_name} - {self.contest.name} (#{self.position})"


class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    subtext = models.CharField(max_length=255)
    icon_type = models.CharField(max_length=50)  # You can map this to FaTrophy, etc.
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"
