package org.example.patterns;
public class LicenseFacadeTest {
    public static void main(String[] args) {
        LicenseFacade f = new LicenseFacade();
        if (!f.submit("x").equals("wrote-license:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
