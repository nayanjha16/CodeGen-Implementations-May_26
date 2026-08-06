package org.example.patterns;
public class SensorsDipTest {
    public static void main(String[] args) {
        String out = new SensorsAppService(new SensorsHttpGateway()).publish("p");
        if (!out.equals("http-sensors:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
