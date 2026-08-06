package org.example.patterns;
public class SensorsMediatorTest {
    public static void main(String[] args) {
        SensorsMediator m = new SensorsMediator();
        new SensorsColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
