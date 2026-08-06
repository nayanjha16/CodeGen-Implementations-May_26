package org.example.patterns;
public class LicenseTemplateTest {
    public static void main(String[] args) {
        String out = new LicenseUpperTemplate().run(" ab ");
        if (!out.equals("license|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
