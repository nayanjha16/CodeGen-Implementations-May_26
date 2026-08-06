package org.example.patterns;
public class SensorsFactoryTest {
    public static void main(String[] args) {
        SensorsFactory f = new SensorsFactory();
        if (!f.create("basic").operate().equals("basic-sensors")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-sensors")) throw new AssertionError();
        System.out.println("ok");
    }
}
