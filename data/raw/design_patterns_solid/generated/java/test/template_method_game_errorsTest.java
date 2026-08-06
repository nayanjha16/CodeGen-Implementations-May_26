package org.example.patterns;
public class GameTemplateTest {
    public static void main(String[] args) {
        String out = new GameUpperTemplate().run(" ab ");
        if (!out.equals("game|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
