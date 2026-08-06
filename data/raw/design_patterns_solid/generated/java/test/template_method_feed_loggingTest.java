package org.example.patterns;
public class FeedTemplateTest {
    public static void main(String[] args) {
        String out = new FeedUpperTemplate().run(" ab ");
        if (!out.equals("feed|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
