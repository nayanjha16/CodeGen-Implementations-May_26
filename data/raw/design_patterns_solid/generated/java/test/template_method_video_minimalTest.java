package org.example.patterns;
public class VideoTemplateTest {
    public static void main(String[] args) {
        String out = new VideoUpperTemplate().run(" ab ");
        if (!out.equals("video|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
