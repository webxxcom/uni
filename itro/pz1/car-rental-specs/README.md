# Car Rental – специфікації обміну даними (ІТРО, ПЗ №1)

Кравченко Р., КНТ-23-1. Предметна область: сервіс оренди автомобілів (Fleet / Customer / Rental Service).

## Запуск

Потрібен лише JDK 21 (Maven завантажиться автоматично через Maven Wrapper):

```
mvnw compile exec:java          (Windows: mvnw.cmd compile exec:java)
```

Програма `Main.java` виконує всі перевірки і пише результати в `output/`:

1. коректність (well-formed) XSD, XML, XSL;
2. дійсність `car-rental.xml` відносно `car-rental.xsd`;
3. генерацію XML на основі XSD (Apache XMLBeans xsd2inst) → `output/car-rental-generated.xml` і його перевірку;
4. перевірку, що схема відхиляє `xml/invalid/car-rental-invalid.xml`;
5. XSLT → `output/car-rental.html` (усі дані) і `output/car-rental-available.html` (фільтр carStatus=AVAILABLE, minDailyRate=1400);
6. валідацію `json/rentals.json` за `json/rentals.schema.json` (draft 2020-12) і відхилення `json/invalid/rentals-invalid.json`.

`car-rental.xml` можна також відкрити в браузері напряму – перетворення підключене інструкцією `xml-stylesheet`
(деякі браузери блокують XSLT для локальних файлів; тоді використовуйте `output/car-rental.html`).

## Файли

| Файл | Призначення |
|---|---|
| `src/main/resources/xml/car-rental.xsd` | XML-схема (простір імен `cr`) |
| `src/main/resources/xml/car-rental.xml` | XML-документ з даними |
| `src/main/resources/xml/car-rental.xsl` | XSLT → HTML |
| `src/main/resources/json/rentals.json` | JSON-документ (відповідь Rental Service) |
| `src/main/resources/json/rentals.schema.json` | JSON Schema |
| `src/main/resources/*/invalid/` | документи з навмисними помилками |
| `src/main/java/ua/nure/kravchenko/carrental/Main.java` | перевірки, генерація, XSLT |
