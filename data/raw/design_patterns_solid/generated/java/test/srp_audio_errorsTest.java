package org.example.patterns;
public class AudioSrpTest {
    public static void main(String[] args) {
        AudioRecord r = new AudioRecord("a", 3);
        if (!new AudioFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
