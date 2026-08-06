package org.example.patterns;
public class ChatTemplateTest {
    public static void main(String[] args) {
        String out = new ChatUpperTemplate().run(" ab ");
        if (!out.equals("chat|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
