package org.example.patterns;
public class AudioProxyTest {
    public static void main(String[] args) {
        if (!new AudioProxy(true).load("1").equals("real-audio:1")) throw new AssertionError();
        if (!new AudioProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
