package org.example.patterns;
public class DatabaseOcpTest {
    public static void main(String[] args) {
        if (new DatabasePriceEngine(new DatabaseTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
