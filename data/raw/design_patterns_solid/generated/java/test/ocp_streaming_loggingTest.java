package org.example.patterns;
public class StreamingOcpTest {
    public static void main(String[] args) {
        if (new StreamingPriceEngine(new StreamingTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
