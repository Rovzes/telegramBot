import logging
from telegram.ext import Application, MessageHandler, filters, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.ext import ApplicationBuilder
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from data import db_session
from data.Forms import Form

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR
)

logger = logging.getLogger(__name__)

# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.


async def start(update, context):
    reply_keyboard = [['/help'],
                      ['/new', '/view', '/delete']]
    await update.message.reply_text(
        """Я приложение для знакомств.
Для начала пользования можете создать свою анкету.
/help - просмотреть команды""",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    )


async def help(update, context):
    await update.message.reply_text(
        """Доступные команды:
/new - создать анкету
/view - просмотреть свою анкету
/delete - удалить анкету
/forms - просмотреть все анкеты""")


async def new(update, context):
    db_sess = db_session.create_session()
    user_id = update.effective_user.id
    form = db_sess.query(Form).filter(Form.user_id == user_id).first()
    if form is not None:
        await update.message.reply_text(
            "У вас уже создана анкета"
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "Новая анкета")
    await update.message.reply_text("Введите своё имя")
    return 1


async def enter_name(update, context):
    await update.message.reply_text("Введите свой возраст")
    context.user_data['name'] = update.message.text
    return 2


async def enter_age(update, context):
    await update.message.reply_text("Введите своё место жительства")
    context.user_data['age'] = update.message.text
    return 3


async def enter_locality(update, context):
    context.user_data['locality'] = update.message.text
    await update.message.reply_text("Загрузите ваше фото")
    return 4


async def enter_photo(update, context):
    context.user_data['photo_id'] = update.message.photo[-1].file_id
    form = Form()
    user_id = update.effective_user.id
    form.user_id = user_id
    form.name = context.user_data['name']
    form.age = context.user_data['age']
    form.locality = context.user_data['locality']
    form.photo_id = context.user_data['photo_id']
    db_sess = db_session.create_session()
    db_sess.add(form)
    db_sess.commit()
    await view(update, context)
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Анкета удалена")
    return ConversationHandler.END


async def view(update, context):
    db_sess = db_session.create_session()
    user_id = update.effective_user.id
    user_form = db_sess.query(Form).filter(Form.user_id == user_id).first()
    if user_form is not None:
        reply_keyboard = [['/help'],
                          ['/forms', '/view', '/delete']]
        await update.message.reply_text(
            "Ваша анкета:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
        await context.bot.sendPhoto(
            update.message.chat_id,
            user_form.photo_id,
            caption=f"""Ваше имя: {user_form.name}
Ваш возраст: {user_form.age}
Место жительства: {user_form.locality}""")
    else:
        await update.message.reply_text(
            "Вы ещё не создали анкету")


async def delete(update, context):
    db_sess = db_session.create_session()
    user_id = update.effective_user.id
    form = db_sess.query(Form).filter(Form.user_id == user_id).first()
    if form is not None:
        reply_keyboard = [['/help'],
                          ['/new', '/view', '/delete']]
        db_sess.delete(form)
        db_sess.commit()
        await update.message.reply_text(
            "Анкета удалена",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True))
    else:
        await update.message.reply_text(
            "Вы ещё не создали анкету")


async def forms(update, context):
    db_sess = db_session.create_session()
    user_id = update.effective_user.id
    form = db_sess.query(Form).filter(Form.user_id == user_id).first()
    if form is not None:
        for form in db_sess.query(Form).filter(Form.user_id != user_id):
            await context.bot.sendPhoto(
                update.message.chat_id,
                form.photo_id,
                caption=f"""Имя: {form.name}
Возраст: {form.age}
Место жительства: {form.locality}""")

    else:
        reply_keyboard = [['/help'],
                          ['/new', '/view', '/delete']]
        await update.message.reply_text(
            "Вы ещё не зарегистрировались",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True))


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    # 5997389892:AAHQpEJurZvGCYbFFpVRid4a9-3CRXMXa2w
    proxy_url = "socks5://user:pass@host:port"

    app = ApplicationBuilder().token("5997389892:AAHQpEJurZvGCYbFFpVRid4a9-3CRXMXa2w").proxy_url(proxy_url).build()
    application = Application.builder().token("5997389892:AAHQpEJurZvGCYbFFpVRid4a9-3CRXMXa2w").build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    register = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('new', new)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_age)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_locality)],
            4: [MessageHandler(filters.PHOTO & ~filters.COMMAND, enter_photo)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(register)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("new", new))
    application.add_handler(CommandHandler("view", view))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("forms", forms))

    # Запускаем приложение.
    db_session.global_init("db/users.db")
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
