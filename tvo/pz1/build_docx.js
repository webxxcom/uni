// Builds КНТ-23-1_Кравченко_ПЗ1.docx. Run: node build_docx.js
// Inline markup in text: *italic*, _{subscript}, ^{superscript} (sub/sup may contain *italic*).
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, PageBreak, LineRuleType,
} = require('docx');

const FONT = 'Times New Roman';
const SIZE = 28; // half-points = 14 pt
const TSIZE = 24; // tables: 12 pt
const INDENT = 709; // 1.25 cm
const LINE = { line: 360, lineRule: LineRuleType.AUTO }; // 1.5

function runs(text, base = {}) {
  const out = [];
  const re = /(\*[^*]+\*|_\{[^}]+\}|\^\{[^}]+\})/g;
  let last = 0, m;
  const push = (t, o) => { if (t) out.push(new TextRun({ text: t, font: FONT, ...base, ...o })); };
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index), {});
    const tok = m[0];
    if (tok[0] === '*') push(tok.slice(1, -1), { italics: true });
    else {
      const inner = tok.slice(2, -1);
      const key = tok[0] === '_' ? { subScript: true } : { superScript: true };
      if (inner.startsWith('*') && inner.endsWith('*')) push(inner.slice(1, -1), { ...key, italics: true });
      else push(inner, key);
    }
    last = m.index + tok.length;
  }
  push(text.slice(last), {});
  return out;
}

const P = (text, opts = {}) => new Paragraph({
  children: runs(text),
  alignment: opts.align ?? AlignmentType.JUSTIFIED,
  indent: opts.noIndent ? undefined : { firstLine: INDENT },
  spacing: { ...LINE, after: 0 },
  keepNext: opts.keepNext,
});
const F = (text) => P(text, { align: AlignmentType.CENTER, noIndent: true }); // displayed formula
// Heading 1 = «ЗВІТ» on the title page, Heading 2 = sections, Heading 3 = subsections.
const H1 = (text, pageBreak = false) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(text), pageBreakBefore: pageBreak });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(text) });
const TCAP = (text) => new Paragraph({ children: runs(text), spacing: { before: 120, after: 60 }, keepNext: true });
const FCAP = (text) => new Paragraph({ children: runs(text), alignment: AlignmentType.CENTER, spacing: { before: 60, after: 120 } });

const border = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(rows, widths, { header = true, leftCols = [] } = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    alignment: AlignmentType.CENTER,
    rows: rows.map((row, ri) => new TableRow({
      cantSplit: true,
      children: row.map((cell, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        borders,
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        children: [new Paragraph({
          alignment: leftCols.includes(ci) && ri > 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          keepNext: ri < rows.length - 1,
          children: runs(String(cell), { size: TSIZE, bold: header && ri === 0 }),
        })],
      })),
    })),
  });
}
const img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER,
  keepNext: true,
  children: [new ImageRun({ type: 'png', data: fs.readFileSync(path.join(__dirname, 'img', file)), transformation: { width: w, height: h } })],
});
const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({ children: [], spacing: LINE }));
const C = (text, bold = false) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: LINE, children: runs(text, { bold }) });

// ---------- title page ----------
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const signCell = (lines, align) => new TableCell({
  width: { size: 4677, type: WidthType.DXA }, borders: noBorders,
  children: lines.map(l => new Paragraph({ alignment: align, spacing: LINE, children: runs(l) })),
});
const title = [
  C('МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ', true),
  C('ХАРКІВСЬКИЙ НАЦІОНАЛЬНИЙ УНІВЕРСИТЕТ РАДІОЕЛЕКТРОНІКИ', true),
  ...blank(1),
  C('Кафедра системотехніки'),
  ...blank(6),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs('ЗВІТ') }),
  C('з практичного заняття №1'),
  C('з дисципліни «Технології високопродуктивних обчислень»'),
  C('на тему: «Аналіз трудомісткості паралельних обчислень»'),
  C('Варіант 9'),
  ...blank(5),
  new Table({
    width: { size: 9354, type: WidthType.DXA }, columnWidths: [4677, 4677], borders: noBorders,
    rows: [new TableRow({ children: [
      signCell(['Виконав:', 'ст. гр. КНТ-23-1', 'Кравченко Р.'], AlignmentType.LEFT),
      signCell(['Перевірив:', 'проф. каф. СТ', 'Міщеряков Ю.В.'], AlignmentType.RIGHT),
    ] })],
  }),
  ...blank(4),
  C('Харків 2026'),
];

// ---------- body ----------
const body = [
  H1('1 МЕТА РОБОТИ', true),
  P('Оволодіння основними навичками аналізу трудомісткості паралельних обчислень на простих арифметичних прикладах, визначення основних характеристик трудомісткості та їх залежності від схеми обчислень та кількості процесорів. Отримання досвіду оцінки трудомісткості паралельних обчислень за допомогою основних теорем.'),

  H1('2 ЗАВДАННЯ'),
  P('Для виразу варіанта 9 побудувати граф «операції-операнди», розрахувати послідовний час виконання *T*_{1} та мінімально досяжний час виконання на паракомп’ютері *T*_{∞}, розрахувати прискорення, ефективність та вартість; згідно з теоремою 5 визначити оптимальну кількість процесорів; побудувати розклади виконання для *p* ≥ *T*_{1}/*T*_{∞} та *p* < *T*_{1}/*T*_{∞} та розрахувати для них прискорення, ефективність і вартість.'),
  P('Вираз (варіант 9):', { keepNext: true }),
  img('formula.png', 378, 55),
  P('Модель обчислень: час виконання будь-якої арифметичної операції дорівнює 1, передача даних між процесорами відбувається миттєво.'),

  H1('3 ХІД ВИКОНАННЯ РОБОТИ'),
  H2('3.1 Схема обчислень'),
  P('Вираз обчислюється без попереднього спрощення. Для зменшення кількості операцій значення 49*a*^{2} отримується як добуток (7*a*)·(7*a*), тобто використовує вже обчислене 7*a*. Останні дві дії виконуються у порядку *A* + (*B* − *C*), що допустимо, бо додавання та віднімання асоціативні; це дозволяє обчислювати *B* − *C* паралельно з *A* і скорочує критичний шлях на одну операцію порівняно з обчисленням зліва направо ((*A* + *B*) − *C*). Перелік операцій наведено в таблиці 3.1.'),
  TCAP('Таблиця 3.1 – Операції алгоритму'),
  table([
    ['№', 'Операція', 'Результат', 'Залежить від', 'Рівень'],
    ['1', '7 · *a*', '7*a*', 'вхідні дані', '1'],
    ['2', '(1) · (1)', '49*a*^{2}', '1', '2'],
    ['3', '1 + (1)', '1 + 7*a*', '1', '2'],
    ['4', '1 − (1)', '1 − 7*a*', '1', '2'],
    ['5', '(2) − 1', '49*a*^{2} − 1', '2', '3'],
    ['6', '(3) ÷ (4)', '(1 + 7*a*)/(1 − 7*a*)', '3, 4', '3'],
    ['7', '(4) ÷ (3)', '(1 − 7*a*)/(1 + 7*a*)', '3, 4', '3'],
    ['8', '4 ÷ (5)', '4/(49*a*^{2} − 1)', '5', '4'],
    ['9', '(6) − (7)', '*B* − *C*', '6, 7', '4'],
    ['10', '(8) + (9)', 'результат', '8, 9', '5'],
  ], [700, 1800, 3000, 1900, 1100]),

  H2('3.2 Граф «операції-операнди»'),
  P('Граф «операції-операнди» алгоритму наведено на рисунку 3.1.', { keepNext: true }),
  img('graph.png', 560, 447),
  FCAP('Рисунок 3.1 – Граф «операції-операнди» (квадрати – вхідні дані, заокруглені прямокутники – операції)'),

  H2('3.3 Час послідовного виконання та мінімальний час виконання'),
  P('Алгоритм містить 10 операцій, кожна з яких виконується за одиницю часу, тому час виконання на одному процесорі:'),
  F('*T*_{1} = 10.'),
  P('За теоремою 1 мінімально можливий час виконання дорівнює довжині максимального (критичного) шляху графа. Критичний шлях: 1 → 2 → 5 → 8 → 10 (а також 1 → 3 → 6 → 9 → 10), його довжина дорівнює 5 операціям:'),
  F('*T*_{∞} = *d*(*G*) = 5.'),

  H2('3.4 Розклад для паракомп’ютера з максимальним рівнем паралелізму'),
  P('Кожна операція виконується одразу, щойно готові її операнди (розклад за рівнями графа). Найбільша кількість операцій на одному рівні дорівнює 3 (рівні 2 і 3), тому *p* = 3. Розклад наведено в таблиці 3.2.'),
  TCAP('Таблиця 3.2 – Розклад для *p* = 3'),
  table([
    ['Процесор \\ такт', '1', '2', '3', '4', '5'],
    ['P1', '1', '2', '5', '8', '10'],
    ['P2', '–', '3', '6', '9', '–'],
    ['P3', '–', '4', '7', '–', '–'],
  ], [2200, 800, 800, 800, 800, 800]),
  P('*T*_{1} = 10, *p* = 3, *T*_{3} = 5;', { noIndent: true }),
  P('*S*_{3} = *T*_{1}/*T*_{3} = 10/5 = 2;', { noIndent: true }),
  P('*E*_{3} = *S*_{3}/*p* = 2/3 ≈ 0,667;', { noIndent: true }),
  P('*C*_{3} = *T*_{3}·*p* = 5·3 = 15.', { noIndent: true }),
  P('Подальше збільшення кількості процесорів не зменшує час виконання, оскільки він уже дорівнює *T*_{∞}: наприклад, при *p* = 4 маємо *T*_{4} = 5, *S*_{4} = 2, *E*_{4} = 0,5, *C*_{4} = 20, тобто лише зростає вартість.'),
  P('*p* = 3 – це також найменша кількість процесорів, за якої досягається час *T*_{∞} = 5: на першому такті готова лише операція 1, на п’ятому – лише операція 10, отже решта 8 операцій мають виконатися за такти 2–4, а для цього потрібно щонайменше ⌈8/3⌉ = 3 процесори. Тому серед розкладів з мінімальним часом виконання розклад з *p* = 3 має мінімальну вартість.'),
  P('Перевірка теореми 3: *T*_{3} = 5 < *T*_{∞} + *T*_{1}/*p* = 5 + 10/3 ≈ 8,33 – виконується.'),

  H2('3.5 Оптимальна кількість процесорів за теоремою 5'),
  P('За теоремою 5 час виконання, порівнянний з мінімально можливим, досягається при кількості процесорів'),
  F('*p* ≈ *T*_{1}/*T*_{∞} = 10/5 = 2,'),
  P('при цьому для *p* ≥ *T*_{1}/*T*_{∞} гарантується *T*_{*p*} ≤ 2·*T*_{∞} = 10.', { noIndent: true }),

  H2('3.6 Розклад для *p* ≥ *T*_{1}/*T*_{∞} (паракомп’ютер зі зменшеним рівнем паралелізму, *p* = 2)'),
  P('Розклад для двох процесорів наведено в таблиці 3.3.'),
  TCAP('Таблиця 3.3 – Розклад для *p* = 2'),
  table([
    ['Процесор \\ такт', '1', '2', '3', '4', '5', '6'],
    ['P1', '1', '2', '4', '6', '8', '10'],
    ['P2', '–', '3', '5', '7', '9', '–'],
  ], [2200, 800, 800, 800, 800, 800, 800]),
  P('Розклад коректний: кожна операція починається після завершення операцій, від яких вона залежить (операція 5 – після 2, операції 6 і 7 – після 3 і 4, операція 8 – після 5, операція 9 – після 6 і 7, операція 10 – після 8 і 9). Коротшого розкладу для двох процесорів не існує: на першому й останньому тактах може виконуватися лише по одній операції (1 і 10), а решта 8 операцій на двох процесорах займають щонайменше 4 такти, тобто *T*_{2} ≥ 1 + 4 + 1 = 6.'),
  P('*T*_{1} = 10, *p* = 2, *T*_{2} = 6;', { noIndent: true }),
  P('*S*_{2} = 10/6 ≈ 1,667;', { noIndent: true }),
  P('*E*_{2} = 1,667/2 ≈ 0,833;', { noIndent: true }),
  P('*C*_{2} = 6·2 = 12.', { noIndent: true }),
  P('Перевірка теореми 5: *T*_{2} = 6 ≤ 2·*T*_{∞} = 10 – виконується. Перевірка теореми 3: 6 < 5 + 10/2 = 10 – виконується.'),

  H2('3.7 Розклад для *p* < *T*_{1}/*T*_{∞} (*p* = 1)'),
  P('Єдина кількість процесорів, менша за *T*_{1}/*T*_{∞} = 2, – це *p* = 1, тобто послідовне виконання операцій у порядку 1, 2, 3, …, 10 (таблиця 3.4).'),
  TCAP('Таблиця 3.4 – Розклад для *p* = 1'),
  table([
    ['Процесор \\ такт', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
    ['P1', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
  ], [2000, 700, 700, 700, 700, 700, 700, 700, 700, 700, 700]),
  P('*T*_{1} = 10, *p* = 1, *T*_{*p*} = 10;', { noIndent: true }),
  P('*S*_{1} = 1; *E*_{1} = 1; *C*_{1} = 10.', { noIndent: true }),
  P('Перевірка теореми 5: *T*_{1}/*p* = 10 ≤ *T*_{*p*} = 10 ≤ 2·*T*_{1}/*p* = 20 – виконується.'),

  H2('3.8 Порівняння розкладів'),
  P('Характеристики отриманих розкладів зведено в таблицю 3.5.'),
  TCAP('Таблиця 3.5 – Характеристики розкладів'),
  table([
    ['*p*', '*T*_{*p*}', '*S*_{*p*}', '*E*_{*p*}', '*C*_{*p*}', 'Примітка'],
    ['1', '10', '1', '1', '10', 'послідовне виконання'],
    ['2', '6', '1,667', '0,833', '12', '*p* = *T*_{1}/*T*_{∞} (теорема 5)'],
    ['3', '5', '2', '0,667', '15', 'максимальний паралелізм, мінімальна вартість при *T*_{*p*} = *T*_{∞}'],
    ['4', '5', '2', '0,5', '20', 'надлишкова кількість процесорів'],
  ], [600, 700, 900, 900, 700, 4700], { leftCols: [5] }),

  H1('4 ВИСНОВКИ'),
  P('У ході роботи для виразу варіанта 9 побудовано граф «операції-операнди», що містить 10 операцій та має критичний шлях довжиною 5, тобто *T*_{1} = 10, *T*_{∞} = 5. Порядок обчислення впливає на трудомісткість: використання 7*a*·7*a* замість окремого обчислення *a*^{2} зменшило кількість операцій, а групування *A* + (*B* − *C*) скоротило критичний шлях з 6 до 5.'),
  P('Мінімальний час виконання *T*_{∞} = 5 досягається на 3 процесорах з прискоренням 2, ефективністю 0,667 та вартістю 15; менша кількість процесорів не дозволяє отримати такий час. За теоремою 5 оптимальна кількість процесорів дорівнює *T*_{1}/*T*_{∞} = 2: на двох процесорах час виконання 6 лише на один такт більший за мінімальний, а ефективність (0,833) вища і вартість (12) менша, ніж на трьох. Подальше збільшення кількості процесорів понад 3 не зменшує час, а лише знижує ефективність і підвищує вартість.'),
  P('Отже, зі зростанням кількості процесорів прискорення обмежене довжиною критичного шляху (*S*_{*p*} ≤ *T*_{1}/*T*_{∞} = 2), а ефективність монотонно спадає. Усі отримані розклади задовольняють оцінки теорем 1, 3 і 5.'),
  P('Також варто зазначити, що вираз можна спростити до −4/(7*a* + 1) (при *a* ≠ ±1/7), що потребує лише 3 послідовних операцій; тобто вибір алгоритму обчислення впливає на трудомісткість значно сильніше, ніж розпаралелювання заданої схеми.'),
];

const doc = new Document({
  creator: 'Кравченко Р.',
  title: 'ТВО ПЗ1 – Аналіз трудомісткості паралельних обчислень',
  styles: {
    default: { document: { run: { font: FONT, size: SIZE } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: '000000' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0, ...LINE }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: SIZE, bold: true, color: '000000', allCaps: true },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 240, after: 240, ...LINE }, keepNext: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: SIZE, bold: true, color: '000000' },
        paragraph: { indent: { firstLine: INDENT }, spacing: { before: 240, after: 120, ...LINE }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1701, right: 851 } } },
    children: [...title, ...body],
  }],
});

Packer.toBuffer(doc).then(buf => {
  const out = path.join(__dirname, 'КНТ-23-1_Кравченко_ПЗ1.docx');
  fs.writeFileSync(out, buf);
  console.log('written', out);
});
