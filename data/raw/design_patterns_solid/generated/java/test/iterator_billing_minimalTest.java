package org.example.patterns;
public class BillingIteratorTest {
    public static void main(String[] args) {
        BillingCollection col = new BillingCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("billing:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
