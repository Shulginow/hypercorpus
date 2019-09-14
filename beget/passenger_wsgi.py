# -*- coding: utf-8 -*-
import sys, os
sys.path.append('/home/v/vstoch2s/alice.botello.ru/Dekart/') # указываем директорию с проектом
sys.path.append('/home/v/vstoch2s/.local/lib/python3.5/site-packages') # указываем директорию с библиотеками, куда поставили Flask
from Dekart import app as application # когда Flask стартует, он ищет application. Если не указать 'as application', сайт не заработает
application.debug = True  # Опционально: True/False устанавливается по необходимости в отладке