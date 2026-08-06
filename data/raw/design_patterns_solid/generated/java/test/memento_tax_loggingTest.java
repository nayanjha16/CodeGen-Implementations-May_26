package org.example.patterns;
public class TaxMementoTest {
    public static void main(String[] args) {
        TaxOriginator o = new TaxOriginator();
        TaxMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("tax-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
