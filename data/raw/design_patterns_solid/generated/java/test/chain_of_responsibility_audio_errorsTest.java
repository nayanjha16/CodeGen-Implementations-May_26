package org.example.patterns;
public class AudioChainTest {
    public static void main(String[] args) {
        AudioHandler h = new AudioLowHandler();
        h.link(new AudioHighHandler());
        if (!h.handle(2, "m").equals("high-audio:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
