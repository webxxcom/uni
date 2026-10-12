# Content of the ІТРО ПЗ №1 report; executed by build_report.py (helpers come from there).

# ---------- title page ----------
C('МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ', True)
C('ХАРКІВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ РАДІОЕЛЕКТРОНІКИ', True)
blank(1)
C('Кафедра системотехніки')
blank(6)
doc.add_paragraph('ЗВІТ', style='Heading 1')
C('з практичного заняття №1')
C('з дисципліни «Internet-технології розподіленої обробки інформації»')
C('на тему: «Розробка специфікацій взаємодії підсистем розподіленого програмного застосування»')
blank(5)
sign = doc.add_table(rows=1, cols=2)
for cell, lines, al in [(sign.cell(0, 0), ['Виконав:', 'ст. гр. КНТ-23-1', 'Кравченко Р.'], WD_ALIGN_PARAGRAPH.LEFT),
                        (sign.cell(0, 1), ['Перевірила:', 'Мірошніченко Н.С.'], WD_ALIGN_PARAGRAPH.RIGHT)]:
    cell.paragraphs[0].text = lines[0]
    cell.paragraphs[0].alignment = al
    for l in lines[1:]:
        cell.add_paragraph(l).alignment = al
blank(5)
C('Харків 2026')

# ---------- 1, 2 ----------
H2('1 МЕТА РОБОТИ')
P('Вивчити стандарти мов XML, XSD та формату JSON / JSON Schema; одержати практичні навички створення XML-документів і XML-схем, що описують дані предметної області розподіленого програмного застосування, перевірки їх коректності та дійсності, генерації XML-документа на основі схеми, перетворення XML у HTML засобами XSLT, а також опису та валідації JSON-даних за допомогою JSON Schema.')

H2('2 ПОСТАНОВКА ЗАДАЧІ', page_break=False)
P('Для обраної предметної області необхідно:')
for t in ['визначити призначення розподіленого програмного застосування та перелік бізнес-процесів (не менше 5 методів API: пошук списку об\'єктів, отримання об\'єкта, додавання, оновлення, видалення);',
          'визначити структуру даних, що передаються між частинами застосування;',
          'створити коректний (well-formed) XML-документ, що містить не менше трьох вкладених сутностей, і наповнити його даними з різними варіантами (обов\'язковість, умови присутності, діапазони значень);',
          'створити XSD-схему, що забезпечує перевірку документа на відповідність вимогам бізнес-процесів, і перевірити дійсність (validation) документа;',
          'згенерувати XML-документ на основі XSD-схеми та порівняти його зі створеним вручну;',
          'розробити XSLT-документ, що перетворює XML-документ у HTML-сторінку;',
          'розробити JSON-файл і JSON Schema для даних предметної області та провести валідацію в онлайн-валідаторі.']:
    bullet(t)

# ---------- 3 ----------
H2('3 ХІД ВИКОНАННЯ РОБОТИ')
H3('3.1 Предметна область і бізнес-процеси')
P('Предметна область – Car Rental, сервіс оренди автомобілів (вільно обрана тема, подана через форму «Вибір предметної області» на курсі). Розподілений веб-застосунок дозволяє клієнтам знаходити вільні автомобілі, бронювати їх на певний період з додатковими послугами та оплачувати оренду, а співробітникам – вести автопарк і облік клієнтів.')
P('Застосування складається з трьох сервісів, кожен з яких зберігає лише свої дані:')
bullet('Fleet Service – автопарк: моделі автомобілів (марка, рік, тип двигуна, кількість місць, добова ставка) та конкретні автомобілі (номерний знак, колір, пробіг, статус);')
bullet('Customer Service – клієнти: ім\'я та прізвище, телефон, e-mail, дата народження, посвідчення водія, персональна знижка;')
bullet('Rental Service – оренди: період, добова ставка на момент оренди, додаткові послуги, загальна вартість, статус і оплата. Під час створення оренди Rental Service звертається до Fleet Service (перевірка доступності автомобіля та отримання ставки) і до Customer Service (перевірка клієнта та його знижки), тобто запит проходить через усі три сервіси.')
P('Перелік бізнес-процесів (методів API) наведено в таблиці 3.1. Для кожного сервісу передбачено мінімальний набір операцій: пошук за критерієм, отримання об\'єкта, додавання (повертає об\'єкт зі збереженим станом), оновлення (повертає об\'єкт з оновленим станом) і видалення. HTTP-методи та шляхи вказано для REST-реалізації в ПЗ №2.')
table_caption('Таблиця 3.1 – Методи API сервісів')
table([['Сервіс', 'Метод', 'HTTP', 'Призначення'],
       ['Fleet', 'findCarModels(searchText)', 'GET /car-models?search=', 'Пошук моделей'],
       ['Fleet', 'getCarModelById(id)', 'GET /car-models/{id}', 'Отримання моделі'],
       ['Fleet', 'findAvailableCars(modelId, startDate, endDate)', 'GET /cars?modelId=&from=&to=', 'Вільні автомобілі на період'],
       ['Fleet', 'getCarById(plateNumber)', 'GET /cars/{plate}', 'Отримання автомобіля'],
       ['Fleet', 'createCar(car)', 'POST /cars', 'Додавання автомобіля'],
       ['Fleet', 'updateCar(plateNumber, car)', 'PUT /cars/{plate}', 'Оновлення статусу, пробігу'],
       ['Fleet', 'deleteCar(plateNumber)', 'DELETE /cars/{plate}', 'Списання автомобіля'],
       ['Customer', 'getAllCustomers(), findCustomerByPhone(phone)', 'GET /customers?phone=', 'Список і пошук клієнтів'],
       ['Customer', 'findCustomerById(id)', 'GET /customers/{id}', 'Отримання клієнта'],
       ['Customer', 'createCustomer(customer)', 'POST /customers', 'Реєстрація клієнта'],
       ['Customer', 'updateCustomer(id, customer)', 'PUT /customers/{id}', 'Оновлення даних і знижки'],
       ['Customer', 'deleteCustomer(id)', 'DELETE /customers/{id}', 'Видалення клієнта'],
       ['Rental', 'getAllRentals(), findRentalsByCustomerId(id)', 'GET /rentals?customerId=', 'Список і пошук оренд'],
       ['Rental', 'findRentalById(id)', 'GET /rentals/{id}', 'Отримання оренди'],
       ['Rental', 'createRental(rental)', 'POST /rentals', 'Бронювання (виклики Fleet і Customer)'],
       ['Rental', 'updateRental(id, rental), payRental(id)', 'PUT /rentals/{id}, POST /rentals/{id}/payment', 'Зміна статусу, оплата'],
       ['Rental', 'cancelRental(id)', 'DELETE /rentals/{id}', 'Скасування оренди']],
      [2.2, 5.6, 5.3, 3.9])

H3('3.2 Структура даних')
P('Дані, що передаються між сервісами, описано шістьма сутностями: CarModel, Car, Customer, Rental, RentalExtra, Payment (таблиця 3.2). Кореневий елемент XML-документа cr:carRental містить три розділи – cr:fleet (Fleet Service), cr:customers (Customer Service) і cr:rentals (Rental Service). Модель містить вкладені автомобілі; оренда містить вкладені додаткові послуги та оплату, а на автомобіль і клієнта посилається атрибутами carPlate та customerId. Ці посилання перевіряються схемою через xsd:key / xsd:keyref, тобто в оренді не можна вказати неіснуючого клієнта чи автомобіль.')
table_caption('Таблиця 3.2 – Сутності та їх поля (обов\'язкові виділено жирним)')
table([['Сутність', 'Поля', 'Обмеження'],
       ['CarModel', '**id**, **brand**, **name**, **year**, **engineType**, **transmission**, **seats**, **dailyRate**, description', 'id = M + 3 цифри; рік 2000…2027; 2–9 місць'],
       ['Car', '**plateNumber**, **color**, **mileage**, **status**, lastServiceDate', 'довільний порядок полів; номер AA0000AA'],
       ['Customer', '**id**, **firstName**, **lastName**, **phoneNumber**, email, **birthDate**, **driverLicense**, discountPercent', 'повнолітній клієнт; знижка 0–30 %'],
       ['Rental', '**id**, **customerId**, **carPlate**, **startDate**, **endDate**, **dailyRate**, extras, **totalCost**, **status**, **payment**', 'посилання на клієнта й автомобіль'],
       ['RentalExtra', '**name**, **price**', '1–5 послуг з переліку; ціна < 1000'],
       ['Payment', 'рівно один варіант: card (maskedNumber, paidAt), cash (receiptNumber, paidAt) або pending (dueDate)', 'xsd:choice / oneOf']],
      [2.6, 9.0, 5.4])
P('Загальна вартість оренди обчислюється як (кількість діб × добова ставка + сума додаткових послуг) × (1 − знижка / 100); у документі, наприклад, для оренди 100001: (5 × 1450 + 150 + 300) × 0,9 = 6930,00 грн.')

H3('3.3 Структура проєкту')
P('Проєкт car-rental-specs – Maven-проєкт (Java 21), який можна відкрити в IntelliJ IDEA або Eclipse і запустити командою mvnw compile exec:java на будь-якому комп\'ютері з JDK 21 (Maven завантажується автоматично через Maven Wrapper). Склад проєкту:')
for t in ['src/main/resources/xml/car-rental.xsd – XML-схема (додаток А);',
          'src/main/resources/xml/car-rental.xml – XML-документ з даними (додаток Б);',
          'src/main/resources/xml/car-rental.xsl – таблиця стилів XSLT (додаток Г);',
          'src/main/resources/xml/invalid/car-rental-invalid.xml – документ з навмисними помилками для перевірки схеми;',
          'src/main/resources/json/rentals.json, rentals.schema.json – JSON-документ і JSON Schema (додатки Д, Е), json/invalid/rentals-invalid.json – JSON з помилками;',
          'src/main/java/…/Main.java – програма, що виконує всі перевірки, генерацію та XSLT-перетворення (додаток Ж);',
          'output/ – результати запуску: згенерований XML (додаток В), HTML-сторінки, журнал перевірок.']:
    bullet(t)

H3('3.4 XSD-схема')
P('Схема (додаток А) визначає простір імен http://nure.ua/knt-23-1/kravchenko/car-rental з префіксом cr (targetNamespace, xmlns:cr, elementFormDefault="qualified"). Відповідність вимогам критеріїв оцінювання наведено в таблиці 3.3.')
table_caption('Таблиця 3.3 – Використання конструкцій XSD')
table([['Вимога', 'Де використано у схемі'],
       ['Простір імен і префікс', 'targetNamespace, xmlns:cr, усі елементи кваліфіковані префіксом cr:'],
       ['minOccurs / maxOccurs', 'carModel (1..unbounded), car (0..50), description і email (0..1), extra (1..5), rental (0..unbounded)'],
       ['minInclusive / maxInclusive', 'ModelYearType ≥ 2000, SeatsType 2..9, MileageType ≤ 999999, BirthDateType 1930-01-01..2008-10-13, discountPercent ≤ 30, generatedAt ≥ 2024-01-01'],
       ['minExclusive / maxExclusive', 'MoneyType > 0, ModelYearType < 2028, ExtraPriceType < 1000'],
       ['length / minLength / maxLength', 'PlateNumberType, PhoneType, DriverLicenseType (length); PersonNameType 1..50, description 10..300, EmailType ≤ 100'],
       ['totalDigits / fractionDigits', 'MoneyType (7 і 2 цифри), RentalIdType (6 цифр)'],
       ['xsd:pattern', 'ідентифікатори M000 / C0000, номерний знак, телефон, e-mail, посвідчення водія, маска картки, номер чека'],
       ['Елементи без restriction', 'brand, name, color (xsd:string), startDate, endDate, lastServiceDate (xsd:date), paidAt (xsd:dateTime)'],
       ['xsd:sequence / xsd:all / xsd:choice', 'CarModelType, CustomerType, RentalType – sequence; CarType – all; PaymentType – choice (card | cash | pending)'],
       ['xsd:enumeration', 'EngineTypeEnum, TransmissionEnum, CarStatusEnum, RentalStatusEnum, ExtraNameType, атрибут source'],
       ['Обов\'язковий атрибут з обмеженням', 'generatedAt (dateTime ≥ 2024-01-01), id, plateNumber, customerId, carPlate, price'],
       ['Необов\'язковий атрибут з обмеженням', 'source (перелік, default="RENTAL_SERVICE"), discountPercent (0..30)'],
       ['Додатково', 'xsd:key / xsd:keyref / xsd:unique – цілісність посилань; xsd:simpleContent / xsd:extension – extra з атрибутом price']],
      [5.0, 12.0])

H3('3.5 XML-документ і перевірка дійсності')
P('XML-документ (додаток Б) містить 4 моделі, 4 автомобілі, 3 клієнтів і 3 оренди. Дані підібрано так, щоб показати можливі варіанти: модель з описом і без, модель без автомобілів; автомобілі з різним порядком полів (xsd:all) і без дати ТО; клієнт без e-mail і знижки; оренда з послугами та без; усі три варіанти оплати (карткою, готівкою, очікує оплати).')
P('Перевірку коректності та дійсності виконує програма Main.java (javax.xml.validation, W3C XML Schema 1.0). Результат наведено на рисунку 3.1: схема, документ і таблиця стилів коректні, схема компілюється без помилок, документ дійсний відносно схеми.')
figure('log-xml.png', 16, 'Рисунок 3.1 – Перевірка коректності та дійсності XSD і XML')
P('Щоб переконатися, що схема дійсно перевіряє вимоги, документ car-rental-invalid.xml містить навмисні помилки (неіснуючий тип двигуна, рік 2030, 12 місць, від\'ємна ціна з трьома знаками після коми, неправильний номерний знак і телефон, неповнолітній клієнт, знижка 45 %, дві оплати одночасно, посилання на неіснуючого клієнта тощо). Схема відхиляє документ і знаходить 38 порушень (рисунок 3.2).')
figure('log-invalid-xml.png', 16.5, 'Рисунок 3.2 – Результат перевірки документа з навмисними помилками')

H3('3.6 Генерація XML-документа на основі XSD і порівняння')
P('XML-документ на основі схеми згенеровано утилітою xsd2inst бібліотеки Apache XMLBeans (аналог команди «Generate XML from XSD» в IDE Eclipse), виклик вбудовано в Main.java. Згенерований документ наведено в додатку В, результат його перевірки – на рисунку 3.3.')
figure('log-generated.png', 16.5, 'Рисунок 3.3 – Перевірка згенерованого XML-документа')
P('Порівняння згенерованого та створеного документів наведено в таблиці 3.4.')
table_caption('Таблиця 3.4 – Порівняння згенерованого та створеного XML-документів')
table([['Ознака', 'Згенерований (xsd2inst)', 'Створений вручну'],
       ['Структура, порядок і вкладеність елементів', 'Збігається зі створеним', 'Збігається зі згенерованим'],
       ['Кратність елементів', 'По одному екземпляру, у коментарях: «1 or more repetitions», «Optional», «0 to 50 repetitions»', '4 моделі, 4 автомобілі, 3 клієнти, 3 оренди; частина необов\'язкових елементів відсутня'],
       ['xsd:choice (оплата)', 'Виведено всі три варіанти одночасно з коментарем «You have a CHOICE of the next 3 items»', 'Рівно один варіант у кожній оренді'],
       ['Значення', 'Заглушки: «string», «token», 1000.000; переліки і числові межі враховано (ELECTRIC, 6 місць, рік 2000)', 'Реальні дані предметної області'],
       ['Дійсність', 'Недійсний: 25 помилок у наведеному запуску (pattern, minInclusive, choice, keyref)', 'Дійсний']],
      [4.2, 6.6, 6.2])
P('Значення-заглушки xsd2inst частково обирає випадково, тому кількість помилок у різних запусках трохи відрізняється (25–27); у додатку В наведено документ того запуску, що й на рисунку 3.3. Розбіжності пояснюються тим, що генератор будує каркас документа за структурою схеми, але не може підібрати значення під регулярні вирази та перехресні посилання. Структура згенерованого документа повністю збігається зі створеним, тобто схема описує саме ту модель даних, яка передбачалася; коригування схеми не знадобилося. Після заміни заглушок реальними значеннями і вибору одного варіанта оплати згенерований документ набуває вигляду створеного.')

H3('3.7 XSLT-перетворення')
P('Таблиця стилів car-rental.xsl (додаток Г) перетворює документ у HTML-сторінку. Використано різні формати подання: заголовки різного розміру, жирний і курсивний шрифт, моноширинний шрифт для сум, таблиці (моделі, автомобілі, оренди), маркований і нумерований списки (вільні автомобілі, клієнти, послуги), абзаци з підсумками (count, sum), сортування (xsl:sort), умовне форматування (xsl:choose, xsl:if, колір статусу), український формат чисел (xsl:decimal-format). Фільтрацію реалізовано параметрами carStatus (статус автомобіля) і minDailyRate (мінімальна ставка), а також фіксованим фільтром «Доступні зараз для оренди». Документ можна відкрити в браузері напряму (інструкція xml-stylesheet) або перетворити програмно (Main.java). Результати наведено на рисунках 3.4 і 3.5.')
figure('xslt-all.png', 16.5, 'Рисунок 3.4 – HTML-сторінка, отримана XSLT-перетворенням (без фільтра)')
figure('xslt-filtered.png', 16.5, 'Рисунок 3.5 – Фільтрація: carStatus = AVAILABLE, minDailyRate = 1400')

H3('3.8 JSON-документ і JSON Schema')
P('JSON-документ rentals.json (додаток Д) – відповідь Rental Service зі списком оренд, у кожну з яких вкладено автомобіль з моделлю, клієнта, масив додаткових послуг і оплату. JSON Schema rentals.schema.json (додаток Е) описана за стандартом draft 2020-12 і використовує:')
for t in ['метадані $schema, $id, title, description; повторно використовувані визначення $defs і посилання $ref;',
          'типи string, integer, number, boolean (через const), null, object, array, у тому числі об\'єднаний тип ["string", "null"] для необов\'язкового e-mail;',
          'обмеження minimum, maximum, exclusiveMinimum, exclusiveMaximum, minLength, maxLength, pattern, format (date, date-time, email), enum, const;',
          'обов\'язкові поля required і заборону зайвих полів additionalProperties: false;',
          'масиви з items, minItems, maxItems, uniqueItems;',
          'oneOf для трьох варіантів оплати (аналог xsd:choice).']:
    bullet(t)
P('Валідацію виконано в онлайн-валідаторі jsonschemavalidator.net (рисунок 3.6) і продубльовано бібліотекою networknt json-schema-validator у Main.java (рисунок 3.8). Для перевірки схеми використано також документ з навмисними помилками – обидва валідатори знайшли в ньому однакову кількість порушень – 25 (рисунки 3.7, 3.8).')
figure('json-online-valid.jpg', 16, 'Рисунок 3.6 – Онлайн-валідація rentals.json: помилок не знайдено')
figure('json-online-invalid.jpg', 16, 'Рисунок 3.7 – Онлайн-валідація rentals-invalid.json: знайдено 25 помилок')
figure('log-json.png', 16.5, 'Рисунок 3.8 – XSLT-перетворення та валідація JSON у Main.java')

H2('4 ВИСНОВКИ')
P('У ході практичного заняття для предметної області «Сервіс оренди автомобілів» визначено три підсистеми розподіленого застосування (Fleet, Customer і Rental Service), їх API з операціями пошуку, отримання, додавання, оновлення та видалення, а також структуру даних із шести сутностей, якими обмінюються сервіси.')
P('Розроблено XSD-схему з простором імен, що використовує всі види обмежень (minOccurs/maxOccurs, min/maxInclusive, min/maxExclusive, length, min/maxLength, totalDigits, fractionDigits, pattern), інструкції sequence, all і choice, переліки, обов\'язкові та необов\'язкові атрибути з обмеженнями, а також перевірку цілісності посилань key/keyref. Створений XML-документ коректний і дійсний; документ з навмисними помилками схема відхиляє (38 порушень). Згенерований на основі схеми документ збігається зі створеним за структурою і відрізняється лише значеннями-заглушками.')
P('Розроблено XSLT-перетворення XML у HTML з таблицями, списками, різними шрифтами, сортуванням і фільтрацією, а також JSON-документ і JSON Schema (draft 2020-12), дійсність яких підтверджено онлайн-валідатором і програмно. Отримані схеми будуть використані як контракти обміну даними між сервісами в наступних практичних заняттях.')

# ---------- appendices ----------
for letter, title, path in [('А', 'XSD-схема car-rental.xsd', 'src/main/resources/xml/car-rental.xsd'),
                            ('Б', 'XML-документ car-rental.xml', 'src/main/resources/xml/car-rental.xml'),
                            ('В', 'XML-документ, згенерований на основі XSD (car-rental-generated.xml)', 'output/car-rental-generated.xml'),
                            ('Г', 'Таблиця стилів XSLT car-rental.xsl', 'src/main/resources/xml/car-rental.xsl'),
                            ('Д', 'JSON-документ rentals.json', 'src/main/resources/json/rentals.json'),
                            ('Е', 'JSON Schema rentals.schema.json', 'src/main/resources/json/rentals.schema.json'),
                            ('Ж', 'Програма перевірок Main.java', 'src/main/java/ua/nure/kravchenko/carrental/Main.java')]:
    H2(f'ДОДАТОК {letter}')
    C(title, bold=True)
    code(path)

doc.core_properties.title = 'ІТРО ПЗ1 – Розробка специфікацій взаємодії підсистем'
doc.core_properties.author = 'Кравченко Р.'
doc.save(OUT)
print('written', OUT)
