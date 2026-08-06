package org.example.patterns;
public class WidgetsOcpTest {
    public static void main(String[] args) {
        if (new WidgetsPriceEngine(new WidgetsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
