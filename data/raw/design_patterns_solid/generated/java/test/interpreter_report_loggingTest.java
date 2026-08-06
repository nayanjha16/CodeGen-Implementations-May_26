package org.example.patterns;
public class ReportInterpreterTest {
    public static void main(String[] args) {
        ReportInterpreter i = new ReportInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
