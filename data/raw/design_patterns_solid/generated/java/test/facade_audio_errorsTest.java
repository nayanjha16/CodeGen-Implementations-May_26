package org.example.patterns;
public class AudioFacadeTest {
    public static void main(String[] args) {
        AudioFacade f = new AudioFacade();
        if (!f.submit("x").equals("wrote-audio:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
