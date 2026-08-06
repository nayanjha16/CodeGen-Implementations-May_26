package org.example.patterns;
public class SensorsOcpTest {
    public static void main(String[] args) {
        if (new SensorsPriceEngine(new SensorsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
