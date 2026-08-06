package org.example.patterns;
public class LicenseInterpreterTest {
    public static void main(String[] args) {
        LicenseInterpreter i = new LicenseInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
