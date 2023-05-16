from telebot import types


main = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=10)
main.row('Афиша')
main.row('Помощь')

error = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
error.row('Задать город', 'Назад')


remove = types.ReplyKeyboardRemove(selective=False)

