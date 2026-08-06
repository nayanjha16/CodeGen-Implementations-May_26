package org.example.patterns;
public class NotesTemplateTest {
    public static void main(String[] args) {
        String out = new NotesUpperTemplate().run(" ab ");
        if (!out.equals("notes|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
