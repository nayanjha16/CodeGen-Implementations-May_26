package org.example.patterns;
public class SensorsFacadeTest {
    public static void main(String[] args) {
        SensorsFacade f = new SensorsFacade();
        if (!f.submit("x").equals("wrote-sensors:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
