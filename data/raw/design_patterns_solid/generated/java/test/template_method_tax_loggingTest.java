package org.example.patterns;
public class TaxTemplateTest {
    public static void main(String[] args) {
        String out = new TaxUpperTemplate().run(" ab ");
        if (!out.equals("tax|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
