package org.example.patterns;
public class SensorsSingletonTest {
    public static void main(String[] args) {
        SensorsSingleton a = SensorsSingleton.getInstance();
        SensorsSingleton b = SensorsSingleton.getInstance();
        a.setValue("sensors-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("sensors-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
