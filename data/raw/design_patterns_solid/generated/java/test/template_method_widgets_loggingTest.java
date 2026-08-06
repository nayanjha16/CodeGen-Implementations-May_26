package org.example.patterns;
public class WidgetsTemplateTest {
    public static void main(String[] args) {
        String out = new WidgetsUpperTemplate().run(" ab ");
        if (!out.equals("widgets|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
