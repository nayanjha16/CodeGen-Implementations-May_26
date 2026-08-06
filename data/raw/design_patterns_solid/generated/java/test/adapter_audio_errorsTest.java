package org.example.patterns;
public class AudioAdapterTest {
    public static void main(String[] args) {
        AudioTarget t = new AudioAdapter(new AudioLegacyApi());
        if (!t.fetch().equals("modern-audio")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
