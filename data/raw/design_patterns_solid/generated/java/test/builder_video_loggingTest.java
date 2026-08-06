package org.example.patterns;
public class VideoBuilderTest {
    public static void main(String[] args) {
        VideoConfig cfg = new VideoConfig.Builder().name("video-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("video-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
