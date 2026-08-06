package org.example.patterns;
public class SensorsVisitorTest {
    public static void main(String[] args) {
        String out = new SensorsLeaf("n").accept(new SensorsPrintVisitor());
        if (!out.equals("sensors:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
