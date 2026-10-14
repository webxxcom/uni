# Content of the РмЗ ПЗ №1 report; executed by build_report.py (helpers come from there).

# ---------- title page ----------
C('МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ', True)
C('ХАРКІВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ РАДІОЕЛЕКТРОНІКИ', True)
blank(1)
C('Кафедра системотехніки')
blank(6)
doc.add_paragraph('ЗВІТ', style='Heading 1')
C('з практичного заняття №1')
C('з дисципліни «Розробка мобільних застосунків»')
C('на тему: «Створення простого мобільного додатка»')
blank(5)
sign = doc.add_table(rows=1, cols=2)
for cell, lines, al in [(sign.cell(0, 0), ['Виконав:', 'ст. гр. КНТ-23-1', 'Кравченко Р.'], WD_ALIGN_PARAGRAPH.LEFT),
                        (sign.cell(0, 1), ['Перевірив:', 'Яцик М.В.'], WD_ALIGN_PARAGRAPH.RIGHT)]:
    cell.paragraphs[0].text = lines[0]
    cell.paragraphs[0].alignment = al
    for l in lines[1:]:
        cell.add_paragraph(l).alignment = al
blank(5)
C('Харків 2026')

# ---------- 1, 2 ----------
H2('1 МЕТА РОБОТИ')
P('Створити простий мобільний додаток за допомогою фреймворку .NET MAUI: вивчити основні можливості та інструменти MAUI, розробити функціонал додатка з використанням шаблону MVVM та елемента компонування TableView, а також інтегрувати його з можливостями платформи (вибір файлів, системний застосунок карт).')

H2('2 ЗАВДАННЯ', page_break=False)
P('Розробити інтерфейс програми для перегляду зображень за допомогою елемента компонування TableView та інших компонентів (приклад – Xaminals з репозиторію dotnet/maui-samples).')
P('Додатково, за рекомендацією з лекції від 14.10.2026, реалізовано читання метаданих фотографії (EXIF) бібліотекою MetadataExtractor: камера, дата зйомки, роздільна здатність та GPS-координати, і показ місця зйомки на карті.')

# ---------- 3 ----------
H2('3 ХІД ВИКОНАННЯ РОБОТИ')
H3('3.1 Функції додатка')
for t in ['галерея: список фотографій у TableView, розбитий на секції «З геолокацією» і «Без геолокації», у кожному рядку – мініатюра, ім\'я файлу, дата, камера та координати;',
          'додавання фотографій через системний діалог вибору файлів (FilePicker, кілька файлів одразу), видалення рядка через контекстне меню, очищення списку;',
          'збереження списку між запусками (Preferences);',
          'сторінка перегляду: зображення, таблиця метаданих (TableView з Intent="Data"), карта з міткою в місці зйомки, кнопки «Відкрити в Картах» (системний застосунок карт) і «Копіювати координати»;',
          'для фото без GPS – пояснення замість карти.']:
    bullet(t)

H3('3.2 Структура проєкту (MVVM)')
P('Проєкт PhotoGallery створено шаблоном dotnet new maui (.NET 10, .NET MAUI 10.0.110). Використано пакети CommunityToolkit.Mvvm (ObservableObject, [ObservableProperty], [RelayCommand]) і MetadataExtractor 2.9.3. Структуру наведено в таблиці 3.1.')
table_caption('Таблиця 3.1 – Структура проєкту')
table([['Файл', 'Шар', 'Призначення'],
       ['Models/PhotoItem.cs', 'Model', 'Дані фотографії та форматовані значення для відображення'],
       ['Services/ExifService.cs', 'Service', 'Читання EXIF і GPS бібліотекою MetadataExtractor'],
       ['ViewModels/MainViewModel.cs', 'ViewModel', 'Список фото, команди «Додати», «Видалити», «Очистити», «Відкрити»; збереження в Preferences'],
       ['ViewModels/PhotoViewModel.cs', 'ViewModel', 'Вибране фото (параметр навігації Shell), HTML карти, відкриття в застосунку карт'],
       ['Views/MainPage.xaml(.cs)', 'View', 'Галерея на TableView; секції будуються з ViewModel'],
       ['Views/PhotoPage.xaml(.cs)', 'View', 'Зображення, TableView з метаданими, WebView з картою'],
       ['AppShell.xaml(.cs), MauiProgram.cs', '—', 'Навігація Shell (маршрут PhotoPage), реєстрація сервісів і сторінок у DI']],
      [5.4, 2.2, 9.4])
P('Сторінки та ViewModel-і створює контейнер залежностей (MauiProgram.cs): ExifService і MainViewModel – Singleton, PhotoViewModel і PhotoPage – Transient. Перехід до перегляду виконується командою OpenCommand: Shell.GoToAsync(nameof(PhotoPage), параметр «Photo»), а ViewModel отримує фото через атрибут [QueryProperty].')

H3('3.3 Галерея на TableView')
P('TableView складається з TableRoot, який містить секції TableSection, а секції – комірки (як у прикладі з методичних вказівок). На відміну від CollectionView, TableView не має властивості ItemsSource, тому секції будуються в коді сторінки (MainPage.xaml.cs) з колекцій ViewModel WithLocation і WithoutLocation і перебудовуються при кожній зміні списку (подія PropertyChanged). Кожен рядок – ViewCell з Grid: мініатюра Image (AspectFill) і три підписи. Натискання на рядок викликає OpenCommand, контекстне меню – RemoveCommand.')
P('На сторінці перегляду метадані виведено «декларативно» в XAML: TableView з Intent="Data", секції «Файл» і «EXIF», комірки TextCell з прив\'язкою Detail до властивостей фото.')
P('Примітка: у .NET 10 елементи TableView, ViewCell і TextCell позначені як застарілі (рекомендовано CollectionView). Оскільки завдання вимагає саме TableView, попередження компілятора CS0618 у проєкті вимкнено свідомо (властивість NoWarn у PhotoGallery.csproj).')

H3('3.4 Читання EXIF і GPS-координат')
P('Формат JPEG зберігає метадані у блоці EXIF, а місце зйомки – у підблоці GPS IFD (широта/довгота у градусах, хвилинах, секундах і півкуля N/S, E/W). ExifService.Read() викликає ImageMetadataReader.ReadMetadata(path) і бере з результату каталоги:')
bullet('ExifIfd0Directory – виробник і модель камери (Make, Model);')
bullet('ExifSubIfdDirectory – дата зйомки DateTimeOriginal (якщо її немає – дата файлу з позначкою «дата файлу»);')
bullet('JpegDirectory – ширина й висота зображення;')
bullet('GpsDirectory – метод TryGetGeoLocation() повертає десяткові широту і довготу з урахуванням півкуль; висота – TagAltitude з урахуванням AltitudeRef.')
P('Читання файлів виконується у фоновому потоці (Task.Run), щоб не блокувати інтерфейс; на час завантаження показується ActivityIndicator. Пошкоджений або нерозпізнаний файл показується без метаданих (ImageProcessingException перехоплюється).')

H3('3.5 Показ місця зйомки на карті')
P('Елемент Map із пакета Microsoft.Maui.Controls.Maps, розглянутий на лекції, працює на Android, iOS і macOS, але не підтримується на Windows. Щоб додаток працював і на ПК, карта реалізована через WebView з бібліотекою Leaflet: формується HTML з міткою (marker) і колом радіусом 100 м у точці зйомки, тайли – Esri World Street Map. Під час налагодження з\'ясовано, що tile.openstreetmap.org і вбудована карта OpenStreetMap блокують запити з WebView (відповіді 403 і 429), а тайли CARTO з 2026 року вимагають ключ API, тому обрано Esri (не потребує ключа, підпис «Tiles © Esri»).')
P('Кнопка «Відкрити в Картах» викликає Map.Default.TryOpenAsync(new Location(lat, lon), new MapLaunchOptions { Name }) – відкривається системний застосунок карт (на Windows – «Карти», на Android – Google Maps, на iOS – Apple Maps). Якщо відкрити не вдалося, показується повідомлення.')

H3('3.6 Збирання та тестування')
P('На комп\'ютері встановлено лише workload maui-windows, тому за замовчуванням проєкт збирається під net10.0-windows10.0.19041.0; Android/iOS вмикаються параметром dotnet build -p:EnableMobile=true (потрібні відповідні workloads). Збирання: dotnet build – без помилок і попереджень.')
P('Для тестування використано три фотографії Nikon COOLPIX P6000 з GPS-даними (набір прикладів ianare/exif-samples) і згенероване зображення без EXIF. Для швидкої демонстрації можна задати змінну середовища PHOTO_GALLERY_FOLDER з текою, фото з якої буде додано під час запуску. Результати наведено на рисунках 3.1–3.3: фотографії правильно розподілено за секціями, з EXIF прочитано камеру, дату зйомки (22.10.2008) і координати (43.466012, 11.879112), мітка на карті – в Ареццо (Італія), на площі, яку видно на знімку; для фото без GPS показано пояснення.')
figure('gallery.png', 16.5, 'Рисунок 3.1 – Галерея: TableView із секціями «З геолокацією» та «Без геолокації»')
figure('photo_gps.png', 16.5, 'Рисунок 3.2 – Перегляд фото: метадані EXIF і місце зйомки на карті')
figure('photo_nogps.png', 16.5, 'Рисунок 3.3 – Перегляд фото без GPS-даних')

H2('4 ВИСНОВКИ')
P('У ході практичного заняття розроблено кросплатформний додаток .NET MAUI для перегляду зображень за шаблоном MVVM. Галерея та таблиця метаданих побудовані на елементі TableView (TableRoot → TableSection → комірки ViewCell/TextCell), навігація – на Shell з передаванням параметра, сторінки й ViewModel-і створюються через DI.')
P('Додатково реалізовано читання EXIF бібліотекою MetadataExtractor: камера, дата зйомки, роздільна здатність і GPS-координати, які показуються на карті та можуть бути відкриті в системному застосунку карт. Оскільки елемент Map не підтримується на Windows, карту виконано через WebView і Leaflet; з\'ясовано обмеження безкоштовних картографічних сервісів для вбудованих WebView. Додаток зібрано та перевірено на Windows; збирання під Android/iOS передбачене, але на цьому ПК не перевірялося.')

# ---------- appendices ----------
for letter, title, path in [('А', 'Models/PhotoItem.cs', 'Models/PhotoItem.cs'),
                            ('Б', 'Services/ExifService.cs', 'Services/ExifService.cs'),
                            ('В', 'ViewModels/MainViewModel.cs', 'ViewModels/MainViewModel.cs'),
                            ('Г', 'ViewModels/PhotoViewModel.cs', 'ViewModels/PhotoViewModel.cs'),
                            ('Д', 'Views/MainPage.xaml і MainPage.xaml.cs', 'Views/MainPage.xaml'),
                            ('Е', 'Views/PhotoPage.xaml', 'Views/PhotoPage.xaml')]:
    H2(f'ДОДАТОК {letter}')
    C(title, bold=True)
    code(path)
    if letter == 'Д':
        P('MainPage.xaml.cs', indent=False)
        code('Views/MainPage.xaml.cs')

doc.core_properties.title = 'РмЗ ПЗ1 – Перегляд зображень (.NET MAUI, TableView, EXIF/GPS)'
doc.core_properties.author = 'Кравченко Р.'
doc.save(OUT)
print('written', OUT)
