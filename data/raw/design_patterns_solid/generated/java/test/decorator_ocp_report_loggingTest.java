package org.example.patterns;
public class ReportDecoratorTest {
    public static void main(String[] args) {
        ReportComponent c = new ReportUpperDecorator(new ReportCore());
        String out = c.process("ab");
        if (!out.equals("REPORT:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
