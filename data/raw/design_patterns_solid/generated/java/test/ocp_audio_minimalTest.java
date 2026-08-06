package org.example.patterns;
public class AudioOcpTest {
    public static void main(String[] args) {
        if (new AudioPriceEngine(new AudioTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
