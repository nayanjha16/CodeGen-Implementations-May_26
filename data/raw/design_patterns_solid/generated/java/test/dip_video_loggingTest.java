package org.example.patterns;
public class VideoDipTest {
    public static void main(String[] args) {
        String out = new VideoAppService(new VideoHttpGateway()).publish("p");
        if (!out.equals("http-video:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
