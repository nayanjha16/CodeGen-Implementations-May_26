package org.example.patterns;
public class VideoProxyTest {
    public static void main(String[] args) {
        if (!new VideoProxy(true).load("1").equals("real-video:1")) throw new AssertionError();
        if (!new VideoProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
