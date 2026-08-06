package org.example.patterns;
public class VideoLspTest {
    public static void main(String[] args) {
        VideoShape[] arr = new VideoShape[] { new VideoRectangle(2,3), new VideoSquare(4) };
        if (VideoLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
