package org.example.patterns;
public class SearchTemplateTest {
    public static void main(String[] args) {
        String out = new SearchUpperTemplate().run(" ab ");
        if (!out.equals("search|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
