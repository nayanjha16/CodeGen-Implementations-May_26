package org.example.patterns;
public class QueueTemplateTest {
    public static void main(String[] args) {
        String out = new QueueUpperTemplate().run(" ab ");
        if (!out.equals("queue|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
