"""Bot that takes attendance on google sheets"""
import logging
import json
from SpreadUtil import column_list_from_cell, find_row, find_date, write_value
import time
import telegram.ext
from telegram import Update
from telegram.ext import Application, CommandHandler, PollAnswerHandler

TOKEN = json.load(open("TelegramTok.json"))["tok"]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update, context) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "\U0001f916 <strong> Vamos a tomar lista!! \n"
        "/TyP1 Lun/Jue 8:00 Hs\n"
        "/TyP2 Mar/Vie 10:00\n"
        "/TyP3 Lun/Jue 14:00\n"
        "/TyP4 Lun/Jue 16:00\n"
        "/Audioperceptiva </strong>", parse_mode=telegram.constants.ParseMode.HTML)


async def poll_lst(update, context):
    """Sends a poll from a student list on the current date"""
    date = time.strftime("%d/%m", time.localtime())
    if "counter" not in context.bot_data:
        course = update.message.text[1:]
        students = column_list_from_cell(course, "A", "2")
        chunks = [students[i:i + 10] for i in range(0, len(students), 10)]
        context.bot_data.update({"counter": 1, "chatid": update.effective_chat.id, "presents": "", "course": course,
                                 "chunks": chunks})
    counter = context.bot_data["counter"]
    if len(context.bot_data["chunks"]) >= counter:
        await context.bot.send_poll(context.bot_data["chatid"], "Asistencia del dia " + date,
                                    context.bot_data["chunks"][counter - 1], is_anonymous=False,
                                    allows_multiple_answers=True)


async def receive_pool_list(update, context):
    """Recibes a poll """
    answer = update.poll_answer
    counter = context.bot_data["counter"]
    course = context.bot_data["course"]
    rows = []
    currentcolumn = find_date(course, "1")
    for i in answer.option_ids:
        student = context.bot_data["chunks"][counter - 1][i]
        context.bot_data["presents"] += "✅" + student + "\n"
        rows.append(find_row(course, "A", student))
    for i in rows:
        write_value(course, "P", currentcolumn, str(i))
    if counter < len(context.bot_data["chunks"]):
        context.bot_data.update({"counter": counter + 1})
        await poll_lst(update, context)
    else:
        presents = context.bot_data["presents"]
        await context.bot.sendMessage(chat_id=context.bot_data["chatid"],
                                      text="\U0001f916 <strong>Listo!! Los presentes son " +
                                           str(len(presents.splitlines())) + ":\n" + presents + "</strong>",
                                      parse_mode=telegram.constants.ParseMode.HTML)
        context.bot_data.clear()


def main() -> None:
    """Run bot."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("TyP1", poll_lst))
    application.add_handler(CommandHandler("TyP2", poll_lst))
    application.add_handler(CommandHandler("TyP3", poll_lst))
    application.add_handler(CommandHandler("TyP4", poll_lst))
    application.add_handler(CommandHandler("Audioperceptiva", poll_lst))
    application.add_handler(PollAnswerHandler(receive_pool_list))
    application.run_polling(allowed_updates=Update.ALL_TYPES) # Run the bot until the user presses Ctrl-C


if __name__ == "__main__":
    main()
