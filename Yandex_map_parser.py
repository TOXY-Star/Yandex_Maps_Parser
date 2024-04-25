from datetime import datetime

import customtkinter as ctk
import logging
from time import sleep
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import customtkinter as ctk
import threading
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep

# Получаем текущую дату и время
now = datetime.now()
# Форматируем дату и время как строку
date_time_str = now.strftime("%Y-%m-%d %H-%M-%S")

# Функция, которая обновляет метку с текущим значением слайдера
def update_slider_value(value):
    slider_label.configure(text=f"Количество заведений: {int(value)}")

# Функция, которая будет работать в отдельном потоке
def selenium_task(city, venue_type, venue_count, output_textbox):


    # ------------------------------------------------------------------------------
    # Установим уровень логирования для всех модулей на WARNING
    logging.basicConfig(level=logging.WARNING)

    options = Options()
    #Скрываем машину
    options.add_argument("--disable-blink-features=AutomationControlled")  # Убрать атрибуты автоматизации
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
    options.add_argument("--disable-extensions")  # Отключить расширения
    options.add_argument("--disable-popup-blocking")  # Отключить блокировку всплывающих окон

    # Отключаем загрузку изображений
    options.add_argument("--disable-images")  # без картинкоа
    options.add_argument("--disable-extensions")  # ????????????
    options.add_argument("--headless")  # без демонстрации браузера
    options.add_argument("window-size=1920x1080")
    options.add_argument("--disable-notifications")  # без уведомлений о ошибках

    driver = Chrome(options=options)

    # Переименовать атрибуты
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",{"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})

    # вводим переменные, для работы программ
    location = city
    title = venue_type
    number_of_units = venue_count

    # Открыть URL
    url = f'https://yandex.ru/maps/213/moscow/search/{location}%20{title}'
    driver.get(url)
    # Открываем ту же ссылку с новым зумом
    #current_url = driver.current_url
    #current_url = current_url.rsplit('=', 1)
    #new_url = current_url[0] + "=" + "13"
    #driver.get(new_url)

    # Скролим ленту заведений виниз
    elements = driver.find_elements(By.CLASS_NAME, "search-business-snippet-view__content")
    n = 0

    output_textbox.configure(state="normal")
    output_textbox.insert("1.0", "Поиск ссылок на заведения")
    output_textbox.configure(state="disabled")

    while len(elements) < number_of_units:
        sleep(1)
        elements1 = len(elements)
        elements = driver.find_elements(By.CLASS_NAME, "search-business-snippet-view__content")
        driver.execute_script("arguments[0].scrollIntoView(true);", elements[-1])
        elements = driver.find_elements(By.CLASS_NAME, "search-business-snippet-view__content")
        elements2 = len(elements)
        # Вывод в output_textbox
        output_textbox.configure(state="normal")
        output_textbox.insert("1.0", f"{elements2} из {number_of_units}\n")
        output_textbox.configure(state="disabled")
        print(f'{elements2} из {number_of_units}')
        # Дополнительный, цикл, если список больше не обновляется, через 30 попыток, цикл отключается
        if elements1 == elements2:
            n = n + 1
            output_textbox.configure(state="normal")
            output_textbox.insert("1.0", f'n = {n}\n')
            output_textbox.configure(state="disabled")
            if n >= 10:
                break
        else:
            n = 0

    # Ожидание элемента до тех пор, пока он не будет найден
    wait = WebDriverWait(driver, 10)  # 10 секунд ожидания
    elements = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-snippet-view__link-overlay._focusable")))

    # Собираем список ссылкок на страницы заведений в yandex Maps
    href_list = []
    for i in elements:
        href = i.get_attribute('href')
        href_list.append(href)

    # Этап сбора данных
    keys = {'href': [], 'name': [], 'adress': [], 'phone': [], 'rate': [], 'rate_count': [], 'site': [],
            'average_bill': []}

    output_textbox.configure(state="normal")
    output_textbox.insert("1.0", "Сбор данных с найденных ссылок")
    output_textbox.configure(state="disabled")

    num = 0
    for i in href_list:
        output_textbox.configure(state="normal")
        output_textbox.insert("1.0", f'{num} из {len(href_list)}\n')
        output_textbox.configure(state="disabled")
        print(f'{num} из {len(href_list)}')
        driver.get(i)
        sourse = driver.page_source
        soup = BeautifulSoup(sourse)
        try:
            keys['href'].append(i)
        except:
            keys['href'].append('null')

        try:
            name = soup.find('h1', class_='orgpage-header-view__header')
            keys['name'].append(name.text)
        except:
            keys['name'].append('null')

        try:
            adress = soup.find('a', class_='orgpage-header-view__address')
            keys['adress'].append(adress.text)
        except:
            keys['adress'].append('null')

        try:
            phone = soup.find('div', class_='orgpage-phones-view__phone-number')
            keys['phone'].append(phone.text)
        except:
            keys['phone'].append('null')

        try:
            rate = soup.find('span', class_='business-rating-badge-view__rating-text')
            keys['rate'].append(rate.text)
        except:
            keys['rate'].append('null')

        try:
            rate_count = soup.find('div', class_='business-header-rating-view__text _clickable')
            keys['rate_count'].append(rate_count.text)
        except:
            keys['rate_count'].append('null')

        try:
            site = soup.find('span', class_='business-urls-view__text')
            keys['site'].append(site.text)
        except:
            keys['site'].append('null')

        try:
            average_bill = soup.find('span', class_='business-features-view__valued-value')
            keys['average_bill'].append(average_bill.text)
        except:
            keys['average_bill'].append('null')
        num = num + 1

    output_textbox.configure(state="normal")
    output_textbox.insert("1.0", f'Готово, можно закрывать\n')
    output_textbox.configure(state="disabled")

    driver.close()

    df = pd.DataFrame(keys)
    df.to_excel(f'{location}-{title}-{date_time_str}.xlsx')


# Функция, которая запускает поток
def start_action():
    city = city_entry.get()
    venue_type = venue_type_entry.get()
    venue_count = int(venue_slider.get())

    # Запускаем Selenium в отдельном потоке
    thread = threading.Thread(
        target=selenium_task,
        args=(city, venue_type, venue_count, output_textbox),
        daemon=True  # Флаг daemon позволяет завершить поток, когда приложение закрывается
    )
    thread.start()


# Создание основного окна
app = ctk.CTk()
app.title("Парсер Yandex Карт")
app.geometry("600x400")  # Увеличен размер окна

# Создание рамки (frame) для элементов управления
control_frame = ctk.CTkFrame(app)
control_frame.pack(side='left', fill='y')  # Выравнивание по левой стороне, заполнение по вертикали

# Виджеты для ввода данных
city_entry = ctk.CTkEntry(control_frame, placeholder_text="Москва")
venue_type_entry = ctk.CTkEntry(control_frame, placeholder_text="Ресторан")

# Слайдер с меткой
venue_slider = ctk.CTkSlider(control_frame, from_=1, to=1000, command=update_slider_value)
venue_slider.pack(pady=10)
slider_label = ctk.CTkLabel(control_frame, text="Количество заведений: 500")
slider_label.pack(pady=10)

# Кнопка запуска действия
start_button = ctk.CTkButton(control_frame, text="Старт", command=start_action)

# Виджет для вывода результата
output_textbox = ctk.CTkTextbox(app,width=400, height=400, state="disabled")

# Расположение виджетов
city_entry.pack()
venue_type_entry.pack()
venue_slider.pack()
slider_label.pack()
start_button.pack()
output_textbox.pack()

# Запуск основного цикла Tkinter
app.mainloop()
