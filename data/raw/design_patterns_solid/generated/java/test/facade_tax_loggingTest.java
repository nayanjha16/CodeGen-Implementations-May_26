package org.example.patterns;
public class TaxFacadeTest {
    public static void main(String[] args) {
        TaxFacade f = new TaxFacade();
        if (!f.submit("x").equals("wrote-tax:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
