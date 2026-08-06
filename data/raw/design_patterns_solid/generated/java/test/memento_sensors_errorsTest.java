package org.example.patterns;
public class SensorsMementoTest {
    public static void main(String[] args) {
        SensorsOriginator o = new SensorsOriginator();
        SensorsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("sensors-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
