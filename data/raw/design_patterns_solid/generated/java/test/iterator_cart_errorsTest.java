package org.example.patterns;
public class CartIteratorTest {
    public static void main(String[] args) {
        CartCollection col = new CartCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("cart:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
