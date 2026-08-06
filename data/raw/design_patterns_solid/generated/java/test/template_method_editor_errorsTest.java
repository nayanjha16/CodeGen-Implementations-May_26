package org.example.patterns;
public class EditorTemplateTest {
    public static void main(String[] args) {
        String out = new EditorUpperTemplate().run(" ab ");
        if (!out.equals("editor|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
