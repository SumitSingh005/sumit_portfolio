from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    image = models.ImageField(
        upload_to='projects/',
        null=True,
        blank=True
    )

    github_link = models.URLField(
        null=True,
        blank=True
    )

    demo_link = models.URLField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
