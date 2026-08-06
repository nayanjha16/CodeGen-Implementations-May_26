package org.example.patterns;
public class VideoFactoryTest {
    public static void main(String[] args) {
        VideoFactory f = new VideoFactory();
        if (!f.create("basic").operate().equals("basic-video")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-video")) throw new AssertionError();
        System.out.println("ok");
    }
}
