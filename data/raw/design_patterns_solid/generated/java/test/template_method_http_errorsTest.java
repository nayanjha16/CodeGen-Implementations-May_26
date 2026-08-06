package org.example.patterns;
public class HttpTemplateTest {
    public static void main(String[] args) {
        String out = new HttpUpperTemplate().run(" ab ");
        if (!out.equals("http|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
