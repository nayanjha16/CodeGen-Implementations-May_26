package org.example.patterns;
public class SensorsSrpTest {
    public static void main(String[] args) {
        SensorsRecord r = new SensorsRecord("a", 3);
        if (!new SensorsFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
