from django.db import models


class Reporter(models.Model):
    full_name = models.CharField(max_length=70)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Article(models.Model):
    pub_date = models.DateField()
    headline = models.CharField(max_length=200)
    content  = models.TextField()
    author   = models.ForeignKey(Reporter, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.headline
