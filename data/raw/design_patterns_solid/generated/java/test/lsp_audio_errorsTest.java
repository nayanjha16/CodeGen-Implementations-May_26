package org.example.patterns;
public class AudioLspTest {
    public static void main(String[] args) {
        AudioShape[] arr = new AudioShape[] { new AudioRectangle(2,3), new AudioSquare(4) };
        if (AudioLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
