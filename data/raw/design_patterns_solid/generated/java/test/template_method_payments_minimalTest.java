package org.example.patterns;
public class PaymentsTemplateTest {
    public static void main(String[] args) {
        String out = new PaymentsUpperTemplate().run(" ab ");
        if (!out.equals("payments|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
