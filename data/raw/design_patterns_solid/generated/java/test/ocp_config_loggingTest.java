package org.example.patterns;
public class ConfigOcpTest {
    public static void main(String[] args) {
        if (new ConfigPriceEngine(new ConfigTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
