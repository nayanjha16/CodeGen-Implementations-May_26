package org.example.patterns;
public class EmailOcpTest {
    public static void main(String[] args) {
        if (new EmailPriceEngine(new EmailTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
