run: # Запуск сервера разработки Django
	cd backend && cd foodgram && python3 manage.py runserver 

makemigrations: #Создание файлов миграции на основе изменений в моделях.
	cd backend && cd foodgram && python3 manage.py makemigrations 

migrate: # Применение миграций и обновление базы данных.
	cd backend && cd foodgram && python3 manage.py migrate 
	
