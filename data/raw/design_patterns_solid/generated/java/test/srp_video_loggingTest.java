package org.example.patterns;
public class VideoSrpTest {
    public static void main(String[] args) {
        VideoRecord r = new VideoRecord("a", 3);
        if (!new VideoFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
