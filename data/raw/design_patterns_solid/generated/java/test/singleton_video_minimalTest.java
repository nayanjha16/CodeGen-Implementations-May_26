package org.example.patterns;
public class VideoSingletonTest {
    public static void main(String[] args) {
        VideoSingleton a = VideoSingleton.getInstance();
        VideoSingleton b = VideoSingleton.getInstance();
        a.setValue("video-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("video-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
