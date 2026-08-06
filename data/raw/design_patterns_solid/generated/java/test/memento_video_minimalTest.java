package org.example.patterns;
public class VideoMementoTest {
    public static void main(String[] args) {
        VideoOriginator o = new VideoOriginator();
        VideoMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("video-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
