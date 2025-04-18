import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand
from aiogram.types import Message
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    logger.error("BOT_TOKEN is not set in the environment variables.")
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

commands = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="cancel", description="Отменить текущее действие"),
]


class Form(StatesGroup):
    waiting_for_fio = State()
    waiting_for_photo = State()


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer_sticker("CAACAgIAAxkBAAIRlWe8zRPhoaoD08dIOYbDrmPhmV55AAJdWwACS9bJSiTwphdkogdfNgQ")
    await asyncio.sleep(0.7)
    await message.answer("Привет!👋 \nНапиши ФИО ребенка, который участвует в конкурсе! 🏆")
    await state.set_state(Form.waiting_for_fio)


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены. ❌")
        return

    await state.clear()
    await message.answer("Действие отменено ❌. Вы можете начать заново, отправив /start.")
    logger.info(f"User {message.from_user.full_name} (ID: {message.from_user.id}) has cancelled the action.")


@dp.message(Form.waiting_for_fio)
async def process_fio(message: Message, state: FSMContext):
    if message.text:
        fio = message.text.strip().title().replace(" ", "_")
        await state.update_data(fio=fio)
        await message.answer(f"Спасибо, я записал ФИО! ✍️ \nТеперь отправь фото 📹. \nЕсли передумаешь, отправь /cancel.")
        await state.set_state(Form.waiting_for_photo)
    else:
        await message.answer("⚠️ Пожалуйста, отправьте ФИО. ⚠️ \nЕсли передумали, отправьте /cancel.")


@dp.message(Form.waiting_for_photo)
async def process_file(message: Message, state: FSMContext):
    if message.photo:
        data = await state.get_data()
        fio = data.get("fio", "unknown")

        photo_file = await bot.get_file(message.photo[-1].file_id)
        file_extension = photo_file.file_path.split('.')[-1]
        photo_path = f"photos/{fio}.{file_extension}"

        os.makedirs("photos", exist_ok=True)

        await bot.download_file(photo_file.file_path, photo_path)
        await message.answer("👏 Отлично! 💾 Фото успешно сохранено!")
        logger.info(f"Photo saved: {photo_path}")

        await state.clear()
    else:
        await message.answer("⚠️ Пожалуйста, отправьте фото (не файлом). ⚠️ \nЕсли передумали, отправьте /cancel.")


@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    logger.error(f"Error in update {update}: {exception}", exc_info=True)
    return True


@dp.message()
async def handle_any(message: Message):
    await message.answer("Я самый крутой в мире бот! 😎\n"
                         "Меня создали для резидентов школы KIBERone.\n"
                         "Я помогаю регистрировать участников конкурса! Давай присоединяйся! 🏆\n"
                         "Для участия/регистрации в конкурсе используйте команду: /start")


async def main():
    logger.info("Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
        exit(0)
    except Exception as e:
        logger.critical(f"Bot stopped with error: {e}", exc_info=True)
        exit(1)
