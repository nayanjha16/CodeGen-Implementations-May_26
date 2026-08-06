package org.example.patterns;
public class ReviewTemplateTest {
    public static void main(String[] args) {
        String out = new ReviewUpperTemplate().run(" ab ");
        if (!out.equals("review|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
