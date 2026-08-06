package org.example.patterns;
public class MapTemplateTest {
    public static void main(String[] args) {
        String out = new MapUpperTemplate().run(" ab ");
        if (!out.equals("map|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
