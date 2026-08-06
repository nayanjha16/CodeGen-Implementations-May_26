package org.example.patterns;
public class DiscountIteratorTest {
    public static void main(String[] args) {
        DiscountCollection col = new DiscountCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("discount:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
