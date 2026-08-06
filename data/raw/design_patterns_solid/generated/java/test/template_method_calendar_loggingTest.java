package org.example.patterns;
public class CalendarTemplateTest {
    public static void main(String[] args) {
        String out = new CalendarUpperTemplate().run(" ab ");
        if (!out.equals("calendar|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
