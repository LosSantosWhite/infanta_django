from django.db import models


class UserProfile(models.Model):
    user_name = models.CharField(max_length=250, verbose_name='Имя пользователя', default='Без user_name')
    chat_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user_name


class Messages(models.Model):
    user = models.ForeignKey(
        to='telegrambot.UserProfile',
        verbose_name='Профиль',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время получения')

    def __str__(self):
        return f'Сообедение {self.pk} от {self.user}'

    class Meta:
        verbose_name = 'Сообщение пользователя'
        verbose_name_plural = 'Сообщения пользователей'
