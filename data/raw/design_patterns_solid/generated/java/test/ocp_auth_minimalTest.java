package org.example.patterns;
public class AuthOcpTest {
    public static void main(String[] args) {
        if (new AuthPriceEngine(new AuthTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
