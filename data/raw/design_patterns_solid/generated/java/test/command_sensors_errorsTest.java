package org.example.patterns;
public class SensorsCommandTest {
    public static void main(String[] args) {
        SensorsCommand cmd = new SensorsActionCommand(new SensorsReceiver(), "x");
        if (!cmd.execute().equals("done-sensors:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
