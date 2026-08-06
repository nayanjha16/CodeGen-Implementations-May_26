package org.example.patterns;
public class AudioTemplateTest {
    public static void main(String[] args) {
        String out = new AudioUpperTemplate().run(" ab ");
        if (!out.equals("audio|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
