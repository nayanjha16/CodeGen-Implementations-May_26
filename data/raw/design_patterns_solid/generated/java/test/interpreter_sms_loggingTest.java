package org.example.patterns;
public class SmsInterpreterTest {
    public static void main(String[] args) {
        SmsInterpreter i = new SmsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
