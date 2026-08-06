package org.example.patterns;
public class BillingIspTest {
    public static void main(String[] args) {
        BillingStore st = new BillingStore();
        st.write("x");
        if (!BillingIspClient.mirror(st).equals("billing:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
