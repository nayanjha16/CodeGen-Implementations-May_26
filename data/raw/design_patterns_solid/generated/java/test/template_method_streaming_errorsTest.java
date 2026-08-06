package org.example.patterns;
public class StreamingTemplateTest {
    public static void main(String[] args) {
        String out = new StreamingUpperTemplate().run(" ab ");
        if (!out.equals("streaming|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
