package org.example.patterns;
public class SessionOcpTest {
    public static void main(String[] args) {
        if (new SessionPriceEngine(new SessionTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
