package ua.nure.kravchenko.carrental;

import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SchemaValidatorsConfig;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.xmlbeans.impl.xsd2inst.SampleXmlUtil;
import org.apache.xmlbeans.SchemaType;
import org.apache.xmlbeans.SchemaTypeSystem;
import org.apache.xmlbeans.XmlBeans;
import org.apache.xmlbeans.XmlObject;
import org.apache.xmlbeans.XmlOptions;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXParseException;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.File;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * ІТРО ПЗ №1 (Car Rental). Виконує всі перевірки практичного заняття:
 * <ol>
 *   <li>коректність (well-formed) XSD і XML;</li>
 *   <li>дійсність (valid) XML відносно XSD;</li>
 *   <li>генерацію XML-документа на основі XSD (Apache XMLBeans xsd2inst) і його перевірку;</li>
 *   <li>перевірку, що XSD відхиляє навмисно некоректний документ;</li>
 *   <li>XSLT-перетворення XML у HTML (з фільтрацією та без);</li>
 *   <li>валідацію JSON за JSON Schema та відхилення некоректного JSON.</li>
 * </ol>
 * Запуск: {@code mvnw compile exec:java}. Результати – у теці {@code output/}.
 */
public class Main {

    private static final Path RES = Path.of("src", "main", "resources");
    private static final Path OUT = Path.of("output");

    public static void main(String[] args) throws Exception {
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        Files.createDirectories(OUT);
        Path xsd = RES.resolve("xml/car-rental.xsd");
        Path xml = RES.resolve("xml/car-rental.xml");
        Path xsl = RES.resolve("xml/car-rental.xsl");

        section("1. Коректність (well-formed)");
        for (Path p : List.of(xsd, xml, xsl)) {
            parseWellFormed(p);
            System.out.println("  OK  " + p.getFileName() + " – well-formed");
        }

        section("2. Дійсність XML відносно XSD");
        Schema schema = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI).newSchema(xsd.toFile());
        System.out.println("  OK  " + xsd.getFileName() + " – схема скомпільована без помилок (valid XSD)");
        report(xml, validateXml(schema, xml));

        section("3. Генерація XML на основі XSD (xsd2inst) і перевірка");
        Path generated = OUT.resolve("car-rental-generated.xml");
        generateFromXsd(xsd, generated);
        System.out.println("  Згенеровано " + generated);
        report(generated, validateXml(schema, generated));

        section("4. Негативна перевірка XML (документ з навмисними помилками)");
        Path invalidXml = RES.resolve("xml/invalid/car-rental-invalid.xml");
        List<String> xmlErrors = validateXml(schema, invalidXml);
        report(invalidXml, xmlErrors);
        if (xmlErrors.isEmpty()) throw new IllegalStateException("Схема мала відхилити некоректний документ");

        section("5. XSLT-перетворення XML -> HTML");
        transform(xml, xsl, OUT.resolve("car-rental.html"), null, null);
        System.out.println("  OK  output/car-rental.html (усі дані)");
        transform(xml, xsl, OUT.resolve("car-rental-available.html"), "AVAILABLE", "1400");
        System.out.println("  OK  output/car-rental-available.html (carStatus=AVAILABLE, minDailyRate=1400)");

        section("6. Валідація JSON за JSON Schema");
        JsonSchema jsonSchema = loadJsonSchema(RES.resolve("json/rentals.schema.json"));
        report(RES.resolve("json/rentals.json"), validateJson(jsonSchema, RES.resolve("json/rentals.json")));
        Path invalidJson = RES.resolve("json/invalid/rentals-invalid.json");
        List<String> jsonErrors = validateJson(jsonSchema, invalidJson);
        report(invalidJson, jsonErrors);
        if (jsonErrors.isEmpty()) throw new IllegalStateException("Схема мала відхилити некоректний JSON");

        section("Усі перевірки виконано");
    }

    private static void section(String title) {
        System.out.println();
        System.out.println("== " + title + " ==");
    }

    private static void report(Path file, List<String> errors) {
        if (errors.isEmpty()) {
            System.out.println("  OK  " + file.getFileName() + " – valid");
        } else {
            System.out.println("  NOT VALID  " + file.getFileName() + " – помилок: " + errors.size());
            errors.forEach(e -> System.out.println("     - " + e));
        }
    }

    private static void parseWellFormed(Path file) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
        f.setNamespaceAware(true);
        f.newDocumentBuilder().parse(file.toFile());
    }

    /** Повертає всі помилки валідації (а не лише першу). */
    private static List<String> validateXml(Schema schema, Path xml) throws Exception {
        List<String> errors = new ArrayList<>();
        Validator validator = schema.newValidator();
        validator.setErrorHandler(new ErrorHandler() {
            public void warning(SAXParseException e) { }
            public void error(SAXParseException e) { errors.add("рядок " + e.getLineNumber() + ": " + e.getMessage()); }
            public void fatalError(SAXParseException e) { error(e); }
        });
        validator.validate(new StreamSource(xml.toFile()));
        return errors;
    }

    /** Генерує екземпляр кореневого елемента carRental за схемою (аналог «Generate XML from XSD» в IDE). */
    private static void generateFromXsd(Path xsd, Path target) throws Exception {
        XmlObject parsed = XmlObject.Factory.parse(xsd.toFile(), new XmlOptions().setLoadLineNumbers().setLoadMessageDigest());
        SchemaTypeSystem sts = XmlBeans.compileXsd(new XmlObject[]{parsed}, XmlBeans.getBuiltinTypeSystem(), new XmlOptions());
        SchemaType root = null;
        for (SchemaType t : sts.documentTypes()) {
            if (t.getDocumentElementName().getLocalPart().equals("carRental")) root = t;
        }
        if (root == null) throw new IllegalStateException("Кореневий елемент carRental не знайдено");
        String sample = SampleXmlUtil.createSampleForType(root);
        Files.writeString(target, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + sample + "\n");
    }

    private static void transform(Path xml, Path xsl, Path html, String carStatus, String minDailyRate) throws Exception {
        Transformer t = TransformerFactory.newInstance().newTransformer(new StreamSource(xsl.toFile()));
        if (carStatus != null) t.setParameter("carStatus", carStatus);
        if (minDailyRate != null) t.setParameter("minDailyRate", minDailyRate);
        t.transform(new StreamSource(xml.toFile()), new StreamResult(html.toFile()));
    }

    private static JsonSchema loadJsonSchema(Path schemaFile) throws Exception {
        JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);
        SchemaValidatorsConfig config = SchemaValidatorsConfig.builder().formatAssertionsEnabled(true).build();
        return factory.getSchema(Files.newInputStream(schemaFile), config);
    }

    private static List<String> validateJson(JsonSchema schema, Path jsonFile) throws Exception {
        JsonNode node = new ObjectMapper().readTree(new File(jsonFile.toString()));
        Set<ValidationMessage> messages = schema.validate(node);
        return messages.stream().map(ValidationMessage::getMessage).sorted().toList();
    }
}
