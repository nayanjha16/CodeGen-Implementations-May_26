package org.example.patterns;
public class CanvasTemplateTest {
    public static void main(String[] args) {
        String out = new CanvasUpperTemplate().run(" ab ");
        if (!out.equals("canvas|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
