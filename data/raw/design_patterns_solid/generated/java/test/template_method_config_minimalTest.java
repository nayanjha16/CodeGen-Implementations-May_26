package org.example.patterns;
public class ConfigTemplateTest {
    public static void main(String[] args) {
        String out = new ConfigUpperTemplate().run(" ab ");
        if (!out.equals("config|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
