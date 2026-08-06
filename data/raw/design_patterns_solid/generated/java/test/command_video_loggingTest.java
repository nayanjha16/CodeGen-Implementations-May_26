package org.example.patterns;
public class VideoCommandTest {
    public static void main(String[] args) {
        VideoCommand cmd = new VideoActionCommand(new VideoReceiver(), "x");
        if (!cmd.execute().equals("done-video:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
