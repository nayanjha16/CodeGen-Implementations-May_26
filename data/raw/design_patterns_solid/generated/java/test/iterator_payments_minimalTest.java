package org.example.patterns;
public class PaymentsIteratorTest {
    public static void main(String[] args) {
        PaymentsCollection col = new PaymentsCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("payments:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
