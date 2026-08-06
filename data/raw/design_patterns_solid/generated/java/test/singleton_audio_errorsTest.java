package org.example.patterns;
public class AudioSingletonTest {
    public static void main(String[] args) {
        AudioSingleton a = AudioSingleton.getInstance();
        AudioSingleton b = AudioSingleton.getInstance();
        a.setValue("audio-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("audio-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
