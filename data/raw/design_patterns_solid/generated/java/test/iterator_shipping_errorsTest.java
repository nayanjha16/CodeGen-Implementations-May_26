package org.example.patterns;
public class ShippingIteratorTest {
    public static void main(String[] args) {
        ShippingCollection col = new ShippingCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("shipping:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
