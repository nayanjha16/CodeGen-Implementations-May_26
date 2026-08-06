package org.example.patterns;
public class DatabaseTemplateTest {
    public static void main(String[] args) {
        String out = new DatabaseUpperTemplate().run(" ab ");
        if (!out.equals("database|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
