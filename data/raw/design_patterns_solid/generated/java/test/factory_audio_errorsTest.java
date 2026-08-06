package org.example.patterns;
public class AudioFactoryTest {
    public static void main(String[] args) {
        AudioFactory f = new AudioFactory();
        if (!f.create("basic").operate().equals("basic-audio")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-audio")) throw new AssertionError();
        System.out.println("ok");
    }
}
