package org.example.patterns;
public class DiscountIspTest {
    public static void main(String[] args) {
        DiscountStore st = new DiscountStore();
        st.write("x");
        if (!DiscountIspClient.mirror(st).equals("discount:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
