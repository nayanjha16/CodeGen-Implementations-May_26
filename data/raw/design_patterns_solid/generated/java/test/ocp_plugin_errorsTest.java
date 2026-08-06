package org.example.patterns;
public class PluginOcpTest {
    public static void main(String[] args) {
        if (new PluginPriceEngine(new PluginTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
