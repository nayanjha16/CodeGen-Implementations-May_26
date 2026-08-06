package org.example.patterns;
public class LoggingTemplateTest {
    public static void main(String[] args) {
        String out = new LoggingUpperTemplate().run(" ab ");
        if (!out.equals("logging|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
