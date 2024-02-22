import telegram.ext
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, Application, CommandHandler, ContextTypes, MessageHandler, filters
from itertools import islice
import logging
import os
from SpreadUtil import column_list, write_value, find_date

Start, Style = range(2)

#logging.basicConfig(filename="log.txt", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                    level=logging.INFO)
#logger = logging.getLogger(__name__)

TOKEN = json.load(open("TelegramTok.json"))["tok"]
#devid = json.load(open("token.json"))["chatid"]
#reconocimientos = json.load(open("reconicimientos.json"))
#teoria = json.load(open("teoria.json"))
application = Application.builder().token(TOKEN).build()
#datos = json.load(open("datos.json"))
#tyc = json.load(open("typ.json"))


def main():
    conv_handler = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler("start", start),
                      telegram.ext.CallbackQueryHandler(pattern="home", callback=start_over),
                      telegram.ext.MessageHandler(telegram.ext.filters.TEXT, handle_message)],
        states={
            Start: [telegram.ext.CallbackQueryHandler(pattern="a", callback=style)],
            Style: [telegram.ext.CallbackQueryHandler(pattern="a", callback=complete_lst),
                    telegram.ext.CallbackQueryHandler(pattern="b", callback=one_at_a_time)]
        },
        fallbacks=[telegram.ext.CallbackQueryHandler(pattern="end", callback=end)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    #application.add_handler(telegram.ext.CommandHandler("stats", stats))
    #application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT, handle_message))
    #application.add_error_handler(error)
    application.run_polling()


async def complete_lst(update, context):
    try:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="<strong>Te voy leyendo la lista y vos me decis...</strong>",
                                                      parse_mode=telegram.constants.ParseMode.HTML)
    except:
        pass
    c = context.user_data
    if len(c) == 1:
        lst = column_list("Hoja 1", "A", 2, 8)
        print(lst)
        c[0] = 0
        for i in lst:
            c[int(lst.index(i)) + 1] = i

    if c[0] < len(c) - 2:
        reply_keyboard = [["Presente", "Ausente", "Comedor", "Casa/Vianda"]]
        await context.bot.sendMessage(text=c[int(c[0] + 1)], chat_id=c[100],
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                      input_field_placeholder="Elegí una opción"))
    else:
        c.clear()
        return await start(update, context)


def one_at_a_time(update, context):
    print("pepe")


async def handle_message(update, context):
    lst_messages = ["Presente", "Ausente", "Comedor", "Casa/Vianda"]
    c = context.user_data
    if update.message.text in lst_messages:
        await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
        write_value("hoja1", update.message.text, find_date("1", "H"), str(c[0] + 2))
        c[0] = c[0] + 1
        return await complete_lst(update, context)
    else:
        await context.bot.sendMessage(chat_id=update.message.chat_id, text="Hola!!! empezá escribiendo /start")


async def start(update, context):
    await update.message.reply_text('🤖')
    first_name = update.message.from_user.first_name
    c = context.user_data
    c[100] = update.message.chat_id
    grados = ["1ro", "2do", "3ro", "4to", "5to", "6to", "7mo"]
    msg = " <strong>Hola {}!! Te voy a ayudar a tomar lista.</strong>" \
          "<strong>Elegí un curso</strong>".format(first_name)
    k = []
    for i in grados:
        k.append([InlineKeyboardButton(text=i + " A", callback_data="a"),
                  InlineKeyboardButton(text=i + " B", callback_data="a"),
                  InlineKeyboardButton(text=i + " C", callback_data="a")])
    reply_markup = InlineKeyboardMarkup(k)
    await context.bot.sendMessage(chat_id=c[100], text=msg, reply_markup=reply_markup,
                                  parse_mode=telegram.constants.ParseMode.HTML)

    return Start



async def style(update, context):
    #await update.callbackquerry.answer()
    c = context.user_data
    msg = " <strong>De que manera queres hacerlo?</strong>"
    k = [[InlineKeyboardButton(text="Pasar la lista completa", callback_data="a")],
         [InlineKeyboardButton(text="Ingresar un alumno", callback_data="b")]]
    reply_markup = InlineKeyboardMarkup(k)
    await update.callback_query.edit_message_text(text=msg, reply_markup=reply_markup,
                                                  parse_mode=telegram.constants.ParseMode.HTML)
    return Style


async def start_over(update, context):
    await update.callback_query.answer()
    await context.bot.sendMessage(chat_id=update.callback_query["message"]["chat"]["id"], text="🤖",
                                  parse_mode=telegram.constants.ParseMode.HTML)
    k = [InlineKeyboardButton(text="Programa", url="https://cmbsas-caba.infd.edu.ar/sitio/nivel-medio/")]
    k2 = []
    for i in json.load(open("datos.json"))["start"]:
        k.append(InlineKeyboardButton(i[0], callback_data=i[1]))
    for i in range(0, len(k), 2):
        k2.append(k[i:i + 2])
    reply_markup = InlineKeyboardMarkup(k2)
    await context.bot.sendMessage(chat_id=update.callback_query["message"]["chat"]["id"],
                                  text="<strong>Empecemos otra vez!!</strong>\n"
                                       "Contame que queres hacer.",
                                  reply_markup=reply_markup, parse_mode=telegram.constants.ParseMode.HTML)
    return Start


async def end(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="\U0001f916 <strong>Nos vemos la próxima!!</strong> \U0001FA97",
                                                  parse_mode=telegram.constants.ParseMode.HTML)
    return ConversationHandler.END





async def error_no_file(update, context):
    await update.callback_query.answer()
    c = context.user_data
    logging.error("No habia materiales en " + str(c))
    if c[0] == "start":
        keyboard = base_key("Volver", c[0], two=True)
    else:
        keyboard = base_key("Volver", c[0], two=False)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text="\U0001f916 <strong>No tengo materiales en esa categoría....\n"
                                                       "Que hacemos?</strong>",
                                                  reply_markup=reply_markup,
                                                  parse_mode=telegram.constants.ParseMode.HTML)


async def error(update, context): # Para cuando usan botoneras viejas y se marea el dicc user_data
    logging.error(str(context.error))
    #await context.bot.sendMessage(chat_id=devid, text="Hubo un error " + str(context.error))
    #await context.bot.sendMessage(chat_id=update.effective_chat.id,
    #                                  text="<strong>🤖 Que papelón!!,\nalgo salió mal..... \n"
    #                                  f"Seguí por acá 👉 /start </strong>", parse_mode=telegram.constants.ParseMode.HTML)
    #return telegram.ext.ConversationHandler.END


async def stats(update, context):
    await update.message.reply_text('🤖')
    first_name = update.message.from_user.first_name
    context.user_data[0] = "start"
    msg = u" <strong>Hola {}!! Aqui están algunos datos del uso del bot.</strong>".format(first_name)
    await context.bot.sendMessage(chat_id=devid, text=msg, parse_mode=telegram.constants.ParseMode.HTML)
    uso = json.load(open("usage.json"))
    refresh_data()
    plot_total_data(uso)
    plot_detail_data(uso)
    plot_pie_data(uso)
    for i in range(3):
        with open("grafico_uso" + str(i) + ".png", "rb") as photo_file:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)
        os.remove("grafico_uso" + str(i) + ".png")
    await context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text="<strong>🤖 No vayas a tipear esto..... \n"
                                f"Seguí por acá 👉 /start </strong>", parse_mode=telegram.constants.ParseMode.HTML)


if __name__ == "__main__":
    main()

