package org.example.patterns;
public class VideoStateTest {
    public static void main(String[] args) {
        VideoContext ctx = new VideoContext();
        if (!ctx.request().equals("was-off-video")) throw new AssertionError();
        if (!ctx.request().equals("was-on-video")) throw new AssertionError();
        System.out.println("ok");
    }
}
