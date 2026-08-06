package org.example.patterns;
public class VideoAdapterTest {
    public static void main(String[] args) {
        VideoTarget t = new VideoAdapter(new VideoLegacyApi());
        if (!t.fetch().equals("modern-video")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
