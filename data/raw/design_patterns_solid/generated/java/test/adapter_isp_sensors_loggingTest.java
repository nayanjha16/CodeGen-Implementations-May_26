package org.example.patterns;
public class SensorsAdapterTest {
    public static void main(String[] args) {
        SensorsTarget t = new SensorsAdapter(new SensorsLegacyApi());
        if (!t.fetch().equals("modern-sensors")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
