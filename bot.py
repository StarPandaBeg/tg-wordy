import asyncio
from datetime import datetime
from io import BytesIO
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from docx import Document as DDocument
from docx.shared import Mm

from bottypes import Message
from db import Database
from func import *

CONFIRM_TEXT = "Подтвердить ✅"

def decorate(func):
    async def f(self, message):
        msg = Message(message)
        return await func(self, msg)
    return f

def gen_markup():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(KeyboardButton(CONFIRM_TEXT))
    return markup

def get_image_height(document):
    section = document.sections[0]
    return (section.page_height - section.top_margin - section.bottom_margin) / 36000

class WordyBot:

    def __init__(self, token, locale):
        self.token = token
        self._ = locale
        self.bot = self._create_bot()
        self.db = Database()

    def _create_bot(self):
        bot = AsyncTeleBot(self.token)
        self._register_callbacks(bot)
        return bot

    def _register_callbacks(self, bot):
        bot.message_handler(commands=["start"])(self._handleStart)
        bot.message_handler(commands=["newdoc"])(self._handleNewDoc)
        bot.message_handler(commands=["finish"])(self._handleFinish)
        bot.message_handler(commands=["cancel"])(self._handleCancel)
        bot.message_handler(commands=["empty"])(self._handleEmpty)
        bot.message_handler(content_types=['photo'])(self._handlePhoto)
        bot.message_handler(content_types=['text'], func=lambda message: message.text == CONFIRM_TEXT)(self._handleTextConfirm)
        bot.message_handler(content_types=['text'])(self._handleText)

    @decorate
    async def _handleStart(self, message):
        await self.bot.reply_to(message.raw, self._["start"].replace("{name}", message.user.first_name), parse_mode="MarkdownV2")
    
    @decorate
    async def _handleNewDoc(self, message):
        self.db.create_cache_for(message.user)
        await self.bot.reply_to(message.raw, self._["newdoc"])

    @decorate
    async def _handleFinish(self, message):
        if not self.db.is_user_prepared(message.user):
            await self.bot.reply_to(message.raw, self._["doc_not_started"])
            return
        if len(self.db.get_prepared_cache(message.user)) == 0:
            await self.bot.reply_to(message.raw, self._["doc_empty"])
            return
        self.db.set_ready_state(message.user, True)
        await self.bot.reply_to(message.raw, self._["choose_name"])

    @decorate
    async def _handleCancel(self, message):
        if not self.db.is_user_prepared(message.user):
            await self.bot.reply_to(message.raw, self._["nothing_to_cancel"], reply_markup=ReplyKeyboardRemove())
            return
        self.db.clear_cache(message.user)
        await self.bot.reply_to(message.raw, self._["cancel"], reply_markup=ReplyKeyboardRemove())

    @decorate
    async def _handleEmpty(self, message):
        if not self.db.get_ready_state(message.user):
            return
        self.db.set_name(message.user, None)
        await self._handleTextConfirm(message.raw)

    @decorate
    async def _handlePhoto(self, message):
        if not self.db.is_user_prepared(message.user):
            await self.bot.reply_to(message.raw, self._["doc_not_started"])
            return
        self.db.prepare(message.user, message)
        await self.bot.reply_to(message.raw, self._["photo_prepared"])

    @decorate
    async def _handleTextConfirm(self, message):
        if not self.db.get_ready_state(message.user):
            return

        mkdir(f"tmp/{message.user.id}")

        out = await self.bot.reply_to(message.raw, self._["wait"])
        doc = DDocument()
        for msg in self.db.get_prepared_cache(message.user):
            await download_image(self.bot, message.user.id, msg.photo, msg.photo_unique_id)
            doc.add_picture(f"tmp/{message.user.id}/{msg.photo_unique_id}.png", height=Mm(get_image_height(doc)))
        f = BytesIO()
        doc.save(f)
        f.seek(0)

        fname = self.db.get_name(message.user)
        fname = fname if fname else "document_"+datetime.now().strftime("%d_%m_%Y__%H_%M_%S")
        
        try:
            await self.bot.edit_message_text(self._["complete"], out.chat.id, out.message_id)
        except:
            out = await self.bot.reply_to(out, self._["complete"])
        await self.bot.send_document(out.chat.id, (f"{fname}.docx", f), reply_to_message_id=out.message_id, caption="Made with @wordypicture_bot", reply_markup=ReplyKeyboardRemove())
    
        self.db.clear_cache(message.user)
        rm_if_exists(f"tmp/{message.user.id}", True)

    @decorate
    async def _handleText(self, message):
        if not self.db.get_ready_state(message.user):
            return
        txt = slugify(message.text, True)
        self.db.set_name(message.user, txt)
        await self.bot.reply_to(message.raw, self._["choosen_name"].replace("{filename}", txt), reply_markup=gen_markup())

    def run(self):
        asyncio.run(self.bot.infinity_polling())