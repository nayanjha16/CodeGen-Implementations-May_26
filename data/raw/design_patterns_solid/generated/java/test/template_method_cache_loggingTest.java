package org.example.patterns;
public class CacheTemplateTest {
    public static void main(String[] args) {
        String out = new CacheUpperTemplate().run(" ab ");
        if (!out.equals("cache|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
