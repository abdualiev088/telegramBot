from multiprocessing.sharedctypes import Value
from bot_settings import dp, bot
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3



connect = sqlite3.connect('users.db')
cursor = connect.cursor()
connect = sqlite3.connect('docs.db')
cursor = connect.cursor()

@dp.message_handler(commands='start')
async def whenStart(message: types.Message):
	await message.answer(f'<b>Hello</b> @{message.from_user.username}')
	await message.answer(text=f'This bot can: \n\n<b>📄 Upload files</b> \n<i>--for this just send file here</i> \n\n<b>🔍 Search word</b> from files \n<i>--for this write a word here</i>')

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS username(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_chat_id INTEGER,
		username CHARACTER 
	)""")
	connect.commit() 

	# check if exists
	people_id = message.from_user.id
	cursor.execute(f"SELECT user_chat_id from username where user_chat_id = {people_id};")
	data = cursor.fetchone()
	if data is None:
		# add values in fields
		chat_id = message.from_user.id
		user_name = message.from_user.username
		cursor.execute("INSERT INTO username(user_chat_id, username) VALUES(?, ?);", (chat_id, user_name))
		connect.commit()
	else:
		pass
		# await bot.send_message(message.from_user.id, "This username is already exist.")
	

import PyPDF2

@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
async def catch_doc(message: types.Message):
	file_id = message.document.file_id
	file = await bot.get_file(file_id)
	file_path = file.file_path
	file_size = message.document.file_size
	file_name = message.document.file_name
	
	await bot.download_file(file_path, f'documents/{file_name}')

	pdfFileObj = open(f'documents/{file_name}', 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
	textFromPdf = ''
	for i in range(0, pdfReader.numPages):
		pageObj = pdfReader.getPage(i).extractText()
		textFromPdf += pageObj
	cursor.execute("""
	CREATE TABLE IF NOT EXISTS docs(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_chat INTEGER,
		docs TEXT,
		textFromPdf TEXT,
		doc_size INTEGER
	)""")
	connect.commit() 

	sqlite_select_query = 'SELECT * from docs' 
	cursor.execute(sqlite_select_query) 
	records = cursor.fetchall() 

	ifExist = 0
	if records != []:	
		for i in records:
			if file_name == i[2] and file_size == i[4]:	
				await message.reply('This document is already saved in database')
				ifExist = 1
				break
		if ifExist == 0:
			cursor.execute("INSERT INTO Docs(user_chat, docs, textFromPdf, doc_size) VALUES(?, ?, ?, ?)", (message.from_user.id, file_name, textFromPdf, file_size)) 
			connect.commit()
			await message.reply('Your document has been uploaded')
	if records == []:
		cursor.execute("INSERT INTO Docs(user_chat, docs, textFromPdf, doc_size) VALUES(?, ?, ?, ?)", (message.from_user.id, file_name, textFromPdf, file_size)) 
		connect.commit()
		await message.reply('Your document has been uploaded')	
	pdfFileObj.close()


	
	# sqlite_select_query = 'SELECT * from docs'
	# cursor.execute(sqlite_select_query)
	# records = cursor.fetchall()
	# for i in records:
	# 	print('id: ', i[0])
	# 	print('chat_id: ', i[1])
	# 	print('docs: ', i[2])
	
	# connect.commit()

	# await message.reply('Your document has been uploaded')	


	

@dp.message_handler(types.Message)
async def find(message: types.Message):
	sqlite_select_query = 'SELECT * from docs'
	cursor.execute(sqlite_select_query)
	records = cursor.fetchall()

	# variables to return
	var = message.text
	list_of_fileNames = []

	for i in records:
		if var in i[3]:
			list_of_fileNames.append(i[2])
		if var not in i[3]:
			continue

	if list_of_fileNames:
		await message.answer(f'✅ Found, this word <b>{message.text}</b> in these files ->' + '\n\n' + '<u>' + '\n\n'.join(list_of_fileNames) + '</u>')
	else:
		await message.answer(f'🚫 Not found, this word <b>{message.text}</b> from files. ')
	connect.commit()



if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)