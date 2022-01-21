from django.core.management.base import BaseCommand
from django.conf import settings
from .scenario import brand_info, emails, emails_description
from telegrambot.models import UserProfile, Messages
from telegram.ext.filters import Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, \
    MessageHandler


def save_to_bd(chat_id, text, user_name=None) -> None:
    user, _ = UserProfile.objects.get_or_create(
        chat_id=chat_id,
        defaults={
            'user_name': user_name,
        }
    )
    Messages(
        user=user,
        text=text,
    ).save()


def send_message(update: Update, context: CallbackContext):
    users = UserProfile.objects.all()
    for user in users:
        try:
            context.bot.send_message(
                text=update.message.text,
                chat_id=user.chat_id,
            )
        except Exception:
            user.active = False
            user.save()
    return ConversationHandler.END


class Command(BaseCommand):
    BRAND, LINK, EMAIL = range(3)
    first = 1
    chat_id = None
    user_name = None
    brand = None

    def start(self, update: Update, context: CallbackContext) -> int:
        self.chat_id = update.message.chat_id
        self.user_name = update.message.from_user.name
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=update.message.text
        )
        update.message.reply_text(f'Здравствуйте, {self.user_name}! \n'
                                  f'/contact - для просмотра контактных данных для брендов ООО "Инфанта" Swandoo™ и '
                                  f'Joie™')

    def get_contacts_scenario(self, update: Update, context: CallbackContext) -> int:

        keyboard = [
            [InlineKeyboardButton("Joie", callback_data='joie')],
            [InlineKeyboardButton("Swandoo", callback_data='swandoo')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.chat_id = update.message.chat_id
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=update.message.text
        )
        update.message.reply_text('Выберите бренд:', reply_markup=reply_markup)
        return self.BRAND

    def get_contacts_scenario_restart(self, update: Updater, context: CallbackContext) -> int:
        query = update.callback_query

        query.answer()
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=query.data
        )
        keyboard = [
            [InlineKeyboardButton("Joie", callback_data='joie')],
            [InlineKeyboardButton("Swandoo", callback_data='swandoo')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Выберите бренд:', reply_markup=reply_markup)
        return self.BRAND

    def brands(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=query.data
        )
        query.answer()
        self.brand = query.data
        keyboard = []
        for name, url in brand_info[self.brand].items():
            keyboard.append([InlineKeyboardButton(text=name, url=url)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        for name, params in emails.items():
            keyboard.append([InlineKeyboardButton(text=name, callback_data=f'{params}')])
        keyboard.append([InlineKeyboardButton(text='Назад', callback_data='back')])
        query.edit_message_text(text=f"Бренд: {self.brand.upper()} \n"
                                     f"Доступные ссылки:", reply_markup=reply_markup)

        return self.LINK

    def send_email(self, update: Updater, context: CallbackContext) -> int:
        query = update.callback_query
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=query.data
        )
        query.answer()

        keyboard = [
            [InlineKeyboardButton(text="Назад", callback_data="prev_menu")],
            [InlineKeyboardButton(text="В главное меню", callback_data="restart")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(text=emails_description[query.data], reply_markup=reply_markup)

        return self.EMAIL

    def back_to_first_menu(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=query.data
        )
        query.answer()
        keyboard = [
            [InlineKeyboardButton("Joie", callback_data='joie')],
            [InlineKeyboardButton("Swandoo", callback_data='swandoo')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text('Выберите бренд:', reply_markup=reply_markup)
        return self.BRAND

    def prev_menu(self, update: Updater, context: CallbackContext) -> int:
        query = update.callback_query
        save_to_bd(
            chat_id=self.chat_id,
            user_name=self.user_name,
            text=query.data
        )
        query.answer()
        keyboard = []
        for name, url in brand_info[self.brand].items():
            keyboard.append([InlineKeyboardButton(text=name, url=url)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        for name, params in emails.items():
            keyboard.append([InlineKeyboardButton(text=name, callback_data=params)])
        keyboard.append([InlineKeyboardButton(text='Назад', callback_data='back')])
        query.edit_message_text(text="Доступные ссылки: ", reply_markup=reply_markup)

        return self.LINK

    def help_command(self, update: Update, context: CallbackContext) -> None:
        save_to_bd(
            chat_id=self.chat_id,
            text=update.message.text
        )
        try:
            UserProfile.objects.get(
                chat_id=update.message.chat_id,
                is_admin=True
            )
            text = '/contacts - контакты/ссылки на страницы Инфанты \n' \
                   '/send_to_all - отправка сообщения ВСЕМ пользователям бота ' \
                   '(как реклама каких-то товаров/ссылок/магазинов)'
        except Exception:
            text = '/contacts - ссылки на страницы соцсетей Joie / Swandoo \n'
        update.message.reply_text(text)

    def send_message_to_all_users(self, update: Update, context: CallbackContext):
        try:
            UserProfile.objects.get(
                chat_id=update.message.chat_id,
                is_admin=True
            )
            update.message.reply_text('Напиши текст сообщения для всех пользователей:')
            return self.first
        except Exception as err:
            pass
        return ConversationHandler.END

    def handle(self, *args, **options):
        updater = Updater(settings.BOT_TOKEN)
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', self.start)
        conv = ConversationHandler(
            entry_points=[CommandHandler('contact', self.get_contacts_scenario)],
            states={
                self.BRAND: [CallbackQueryHandler(self.brands), ],
                self.LINK: [CallbackQueryHandler(self.get_contacts_scenario_restart, pattern="^restart$"),
                            CallbackQueryHandler(self.back_to_first_menu, pattern="^back$"),
                            CallbackQueryHandler(self.send_email)],
                self.EMAIL: [CallbackQueryHandler(self.prev_menu, pattern="^prev_menu$"),
                             CallbackQueryHandler(self.get_contacts_scenario_restart, pattern="^restart$")]
            },
            fallbacks=[CommandHandler("contact", self.get_contacts_scenario)]
        )

        dispatcher.add_handler(CommandHandler('help', self.help_command))
        send_message_to_all_handler = ConversationHandler(
            entry_points=[CommandHandler('send_to_all', self.send_message_to_all_users)],
            states={
                self.first: [MessageHandler(filters=Filters.text, callback=send_message)],
            },
            fallbacks=[CommandHandler("send_to_all", self.send_message_to_all_users)]
        )
        handlers = [conv, send_message_to_all_handler, start_handler]
        for handler in handlers:
            dispatcher.add_handler(handler)
        updater.start_polling()
        updater.idle()
