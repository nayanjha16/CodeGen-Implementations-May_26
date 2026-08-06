package org.example.patterns;
public class BookingTemplateTest {
    public static void main(String[] args) {
        String out = new BookingUpperTemplate().run(" ab ");
        if (!out.equals("booking|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
