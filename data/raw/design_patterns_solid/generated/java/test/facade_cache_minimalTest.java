package org.example.patterns;
public class CacheFacadeTest {
    public static void main(String[] args) {
        CacheFacade f = new CacheFacade();
        if (!f.submit("x").equals("wrote-cache:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
