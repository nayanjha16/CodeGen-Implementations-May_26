package org.example.patterns;
public class AudioPrototypeTest {
    public static void main(String[] args) {
        AudioPrototype a = new AudioPrototype("audio", 2);
        AudioPrototype b = a.copy();
        b.setLabel("audio-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
