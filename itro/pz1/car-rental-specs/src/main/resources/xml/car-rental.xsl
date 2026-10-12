<?xml version="1.0" encoding="UTF-8"?>
<!--
  XSLT-перетворення car-rental.xml у HTML-сторінку.
  Параметри фільтрації (можна передати з Java або залишити значення за замовчуванням):
    carStatus    – показати лише автомобілі з цим статусом (ALL – усі);
    minDailyRate – показати лише моделі з добовою ставкою не нижче заданої.
-->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:cr="http://nure.ua/knt-23-1/kravchenko/car-rental"
                exclude-result-prefixes="cr">

    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    <!-- Український формат чисел: 2 900,50 -->
    <xsl:decimal-format name="ua" decimal-separator="," grouping-separator=" "/>

    <xsl:param name="carStatus" select="'ALL'"/>
    <xsl:param name="minDailyRate" select="0"/>

    <xsl:template match="/cr:carRental">
        <html lang="uk">
            <head>
                <meta charset="UTF-8"/>
                <title>Car Rental – дані сервісу оренди</title>
                <style>
                    body { font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; margin: 24px; color: #222; }
                    h1 { font-size: 26px; color: #1f4e9c; }
                    h2 { font-size: 20px; border-bottom: 2px solid #1f4e9c; padding-bottom: 4px; margin-top: 32px; }
                    table { border-collapse: collapse; margin: 8px 0 16px; }
                    th, td { border: 1px solid #999; padding: 4px 10px; }
                    th { background: #e3ebf7; }
                    .meta { font-style: italic; color: #666; font-size: 12px; }
                    .money { text-align: right; font-family: Consolas, monospace; }
                    .AVAILABLE { color: #1b7f2a; font-weight: bold; }
                    .RENTED { color: #b36b00; font-weight: bold; }
                    .MAINTENANCE { color: #b00020; font-weight: bold; }
                    .note { font-size: 12px; color: #555; }
                </style>
            </head>
            <body>
                <h1>Сервіс оренди автомобілів</h1>
                <p class="meta">
                    Документ сформовано: <xsl:value-of select="@generatedAt"/>,
                    джерело: <xsl:value-of select="@source"/>.
                </p>
                <p>
                    У автопарку <b><xsl:value-of select="count(cr:fleet/cr:carModel)"/></b> моделей і
                    <b><xsl:value-of select="count(cr:fleet/cr:carModel/cr:car)"/></b> автомобілів,
                    зареєстровано <b><xsl:value-of select="count(cr:customers/cr:customer)"/></b> клієнтів та
                    <b><xsl:value-of select="count(cr:rentals/cr:rental)"/></b> оренд.
                </p>

                <h2>Моделі автомобілів</h2>
                <p class="note">Фільтр: добова ставка ≥ <xsl:value-of select="$minDailyRate"/> грн; сортування за ставкою.</p>
                <table>
                    <tr><th>ID</th><th>Марка і модель</th><th>Рік</th><th>Двигун</th><th>КПП</th><th>Місць</th><th>Ставка, грн/доба</th></tr>
                    <xsl:for-each select="cr:fleet/cr:carModel[number(cr:dailyRate) &gt;= number($minDailyRate)]">
                        <xsl:sort select="cr:dailyRate" data-type="number" order="descending"/>
                        <tr>
                            <td><xsl:value-of select="@id"/></td>
                            <td><b><xsl:value-of select="cr:brand"/></b>&#160;<xsl:value-of select="cr:name"/></td>
                            <td><xsl:value-of select="cr:year"/></td>
                            <td><xsl:value-of select="cr:engineType"/></td>
                            <td><xsl:value-of select="cr:transmission"/></td>
                            <td><xsl:value-of select="cr:seats"/></td>
                            <td class="money"><xsl:value-of select="format-number(cr:dailyRate, '# ##0,00', 'ua')"/></td>
                        </tr>
                    </xsl:for-each>
                </table>

                <h2>Автомобілі</h2>
                <p class="note">Фільтр за статусом: <b><xsl:value-of select="$carStatus"/></b>.</p>
                <table>
                    <tr><th>Номер</th><th>Модель</th><th>Колір</th><th>Пробіг, км</th><th>Статус</th><th>Останнє ТО</th></tr>
                    <xsl:for-each select="cr:fleet/cr:carModel/cr:car[$carStatus = 'ALL' or cr:status = $carStatus]">
                        <tr>
                            <td><xsl:value-of select="@plateNumber"/></td>
                            <td><xsl:value-of select="concat(../cr:brand, ' ', ../cr:name)"/></td>
                            <td><xsl:value-of select="cr:color"/></td>
                            <td class="money"><xsl:value-of select="format-number(cr:mileage, '# ##0', 'ua')"/></td>
                            <td class="{cr:status}"><xsl:value-of select="cr:status"/></td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="cr:lastServiceDate"><xsl:value-of select="cr:lastServiceDate"/></xsl:when>
                                    <xsl:otherwise><i>немає даних</i></xsl:otherwise>
                                </xsl:choose>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
                <p>Доступні зараз для оренди:</p>
                <ul>
                    <xsl:for-each select="cr:fleet/cr:carModel/cr:car[cr:status = 'AVAILABLE']">
                        <li><b><xsl:value-of select="@plateNumber"/></b> – <xsl:value-of select="concat(../cr:brand, ' ', ../cr:name)"/></li>
                    </xsl:for-each>
                </ul>

                <h2>Клієнти</h2>
                <ol>
                    <xsl:for-each select="cr:customers/cr:customer">
                        <xsl:sort select="cr:lastName"/>
                        <li>
                            <b><xsl:value-of select="concat(cr:lastName, ' ', cr:firstName)"/></b>
                            (<xsl:value-of select="@id"/>), тел. <xsl:value-of select="cr:phoneNumber"/>
                            <xsl:if test="cr:email">, <i><xsl:value-of select="cr:email"/></i></xsl:if>
                            <xsl:if test="@discountPercent &gt; 0"> – знижка <b><xsl:value-of select="@discountPercent"/>%</b></xsl:if>
                        </li>
                    </xsl:for-each>
                </ol>

                <h2>Оренди</h2>
                <table>
                    <tr><th>№</th><th>Клієнт</th><th>Автомобіль</th><th>Період</th><th>Додаткові послуги</th><th>Сума, грн</th><th>Статус</th><th>Оплата</th></tr>
                    <xsl:for-each select="cr:rentals/cr:rental">
                        <xsl:variable name="cid" select="@customerId"/>
                        <xsl:variable name="customer" select="/cr:carRental/cr:customers/cr:customer[@id = $cid]"/>
                        <tr>
                            <td><xsl:value-of select="@id"/></td>
                            <td><xsl:value-of select="concat($customer/cr:lastName, ' ', $customer/cr:firstName)"/></td>
                            <td><xsl:value-of select="@carPlate"/></td>
                            <td><xsl:value-of select="concat(cr:startDate, ' – ', cr:endDate)"/></td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="cr:extras">
                                        <ul>
                                            <xsl:for-each select="cr:extras/cr:extra">
                                                <li><xsl:value-of select="."/> (<xsl:value-of select="@price"/>)</li>
                                            </xsl:for-each>
                                        </ul>
                                    </xsl:when>
                                    <xsl:otherwise>—</xsl:otherwise>
                                </xsl:choose>
                            </td>
                            <td class="money"><xsl:value-of select="format-number(cr:totalCost, '# ##0,00', 'ua')"/></td>
                            <td><xsl:value-of select="cr:status"/></td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="cr:payment/cr:card">Картка <xsl:value-of select="cr:payment/cr:card/cr:maskedNumber"/></xsl:when>
                                    <xsl:when test="cr:payment/cr:cash">Готівка, чек <xsl:value-of select="cr:payment/cr:cash/cr:receiptNumber"/></xsl:when>
                                    <xsl:otherwise><i>Очікує оплати до <xsl:value-of select="cr:payment/cr:pending/@dueDate"/></i></xsl:otherwise>
                                </xsl:choose>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
                <p>
                    Загальна сума оплачених оренд:
                    <b><xsl:value-of select="format-number(sum(cr:rentals/cr:rental[cr:payment/cr:card or cr:payment/cr:cash]/cr:totalCost), '# ##0,00', 'ua')"/> грн</b>.
                </p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
