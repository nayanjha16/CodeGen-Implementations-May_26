package org.example.patterns;
public class TaxMediatorTest {
    public static void main(String[] args) {
        TaxMediator m = new TaxMediator();
        new TaxColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
